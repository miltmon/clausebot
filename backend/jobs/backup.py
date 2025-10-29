"""
ClauseBot Automated Backup System
Runs daily via Render cron to backup critical data

Schedule: 02:00 UTC (via render.yaml)
Backup targets:
  - Supabase quiz_items table
  - Airtable snapshot (optional)
  - Configuration metadata

Storage: S3-compatible (Backblaze B2, AWS S3, DigitalOcean Spaces)
Retention: 30 days (configurable)
"""
import os
import sys
import json
import gzip
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from supabase import create_client, Client


# Configuration
BACKUP_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
BACKUP_STORAGE = os.getenv("BACKUP_STORAGE", "local")  # "local", "s3", "b2"


def get_supabase() -> Client:
    """Create Supabase client."""
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_KEY"]
    return create_client(url, key)


def backup_supabase_table(sb: Client, table_name: str) -> Dict[str, Any]:
    """
    Backup a Supabase table to JSON.
    
    Args:
        sb: Supabase client
        table_name: Table to backup
    
    Returns:
        Dict with data and metadata
    """
    print(f"📥 Backing up table: {table_name}")
    
    try:
        # Fetch all records
        result = sb.table(table_name).select("*").execute()
        data = result.data
        
        print(f"   ✅ Fetched {len(data)} records")
        
        return {
            "table": table_name,
            "timestamp": datetime.utcnow().isoformat(),
            "record_count": len(data),
            "records": data
        }
    
    except Exception as e:
        print(f"   ❌ Backup failed: {e}")
        return {
            "table": table_name,
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "record_count": 0,
            "records": []
        }


def backup_airtable_metadata() -> Dict[str, Any]:
    """
    Backup Airtable configuration metadata.
    Stores base ID, table names, view names for disaster recovery.
    """
    print("📥 Backing up Airtable metadata")
    
    metadata = {
        "timestamp": datetime.utcnow().isoformat(),
        "base_id": os.getenv("AIRTABLE_BASE_ID"),
        "clauses_table": os.getenv("AIRTABLE_CLAUSES_TABLE"),
        "editions_table": os.getenv("AIRTABLE_EDITIONS_TABLE"),
        "view": os.getenv("AIRTABLE_VIEW"),
    }
    
    print(f"   ✅ Metadata captured")
    return metadata


def compress_backup(data: Dict[str, Any]) -> bytes:
    """Compress backup data using gzip."""
    json_str = json.dumps(data, indent=2)
    return gzip.compress(json_str.encode('utf-8'))


def save_backup_local(filename: str, data: bytes) -> str:
    """Save backup to local filesystem (for testing or local storage)."""
    backup_dir = os.getenv("BACKUP_DIR", "./backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    filepath = os.path.join(backup_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(data)
    
    print(f"💾 Saved backup locally: {filepath}")
    return filepath


def save_backup_s3(filename: str, data: bytes) -> str:
    """
    Save backup to S3-compatible storage.
    
    Supports:
    - AWS S3
    - Backblaze B2
    - DigitalOcean Spaces
    - Any S3-compatible provider
    
    Required env vars:
    - BACKUP_BUCKET: Bucket name
    - BACKUP_ACCESS_KEY: Access key ID
    - BACKUP_SECRET_KEY: Secret access key
    - BACKUP_ENDPOINT: Optional endpoint URL (for non-AWS S3)
    - BACKUP_REGION: Optional region (default: us-east-1)
    """
    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError:
        print("❌ boto3 not installed. Install with: pip install boto3")
        return save_backup_local(filename, data)
    
    bucket = os.getenv("BACKUP_BUCKET")
    if not bucket:
        print("⚠️  BACKUP_BUCKET not set, falling back to local storage")
        return save_backup_local(filename, data)
    
    # Configure S3 client
    s3_config = {
        "aws_access_key_id": os.getenv("BACKUP_ACCESS_KEY"),
        "aws_secret_access_key": os.getenv("BACKUP_SECRET_KEY"),
        "region_name": os.getenv("BACKUP_REGION", "us-east-1")
    }
    
    # Add custom endpoint if specified (for non-AWS S3)
    endpoint_url = os.getenv("BACKUP_ENDPOINT")
    if endpoint_url:
        s3_config["endpoint_url"] = endpoint_url
    
    try:
        s3 = boto3.client('s3', **s3_config)
        
        # Upload with server-side encryption
        s3.put_object(
            Bucket=bucket,
            Key=f"clausebot/{filename}",
            Body=data,
            ServerSideEncryption='AES256',
            Metadata={
                'created': datetime.utcnow().isoformat(),
                'service': 'clausebot-backup'
            }
        )
        
        url = f"s3://{bucket}/clausebot/{filename}"
        print(f"☁️  Uploaded backup to S3: {url}")
        return url
    
    except ClientError as e:
        print(f"❌ S3 upload failed: {e}")
        print("⚠️  Falling back to local storage")
        return save_backup_local(filename, data)


def cleanup_old_backups_local(retention_days: int):
    """Delete local backups older than retention period."""
    backup_dir = os.getenv("BACKUP_DIR", "./backups")
    if not os.path.exists(backup_dir):
        return
    
    cutoff = datetime.utcnow() - timedelta(days=retention_days)
    deleted = 0
    
    for filename in os.listdir(backup_dir):
        filepath = os.path.join(backup_dir, filename)
        
        # Check file age
        file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        if file_time < cutoff:
            os.remove(filepath)
            deleted += 1
    
    if deleted > 0:
        print(f"🗑️  Deleted {deleted} old local backups (>{retention_days} days)")


def cleanup_old_backups_s3(retention_days: int):
    """Delete S3 backups older than retention period."""
    try:
        import boto3
        from botocore.exceptions import ClientError
    except ImportError:
        return
    
    bucket = os.getenv("BACKUP_BUCKET")
    if not bucket:
        return
    
    s3_config = {
        "aws_access_key_id": os.getenv("BACKUP_ACCESS_KEY"),
        "aws_secret_access_key": os.getenv("BACKUP_SECRET_KEY"),
        "region_name": os.getenv("BACKUP_REGION", "us-east-1")
    }
    
    endpoint_url = os.getenv("BACKUP_ENDPOINT")
    if endpoint_url:
        s3_config["endpoint_url"] = endpoint_url
    
    try:
        s3 = boto3.client('s3', **s3_config)
        
        # List objects with clausebot prefix
        response = s3.list_objects_v2(
            Bucket=bucket,
            Prefix="clausebot/"
        )
        
        cutoff = datetime.utcnow() - timedelta(days=retention_days)
        deleted = 0
        
        for obj in response.get('Contents', []):
            if obj['LastModified'].replace(tzinfo=None) < cutoff:
                s3.delete_object(Bucket=bucket, Key=obj['Key'])
                deleted += 1
        
        if deleted > 0:
            print(f"🗑️  Deleted {deleted} old S3 backups (>{retention_days} days)")
    
    except ClientError as e:
        print(f"⚠️  S3 cleanup failed (non-fatal): {e}")


def main():
    """Main backup routine."""
    print("🔄 ClauseBot Automated Backup")
    print("="*60)
    print(f"⏰ Started at: {datetime.utcnow().isoformat()}")
    print(f"💾 Storage: {BACKUP_STORAGE}")
    print(f"📅 Retention: {BACKUP_RETENTION_DAYS} days")
    print("="*60)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    try:
        sb = get_supabase()
        
        # Backup Supabase tables
        backups = {
            "quiz_items": backup_supabase_table(sb, "quiz_items"),
            "airtable_metadata": backup_airtable_metadata(),
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0"
        }
        
        # Compress backup
        print("\n🗜️  Compressing backup...")
        compressed = compress_backup(backups)
        original_size = len(json.dumps(backups))
        compressed_size = len(compressed)
        ratio = (1 - compressed_size / original_size) * 100
        print(f"   ✅ Compressed {original_size:,} → {compressed_size:,} bytes ({ratio:.1f}% reduction)")
        
        # Save backup
        filename = f"clausebot_backup_{timestamp}.json.gz"
        
        if BACKUP_STORAGE == "s3":
            save_backup_s3(filename, compressed)
        else:
            save_backup_local(filename, compressed)
        
        # Cleanup old backups
        print("\n🗑️  Cleaning up old backups...")
        if BACKUP_STORAGE == "s3":
            cleanup_old_backups_s3(BACKUP_RETENTION_DAYS)
        else:
            cleanup_old_backups_local(BACKUP_RETENTION_DAYS)
        
        # Summary
        total_records = sum(
            b.get("record_count", 0) 
            for b in backups.values() 
            if isinstance(b, dict) and "record_count" in b
        )
        
        print("\n" + "="*60)
        print("✅ BACKUP COMPLETE")
        print("="*60)
        print(f"  Total records: {total_records:,}")
        print(f"  Compressed size: {compressed_size:,} bytes")
        print(f"  Filename: {filename}")
        print(f"⏰ Finished at: {datetime.utcnow().isoformat()}")
    
    except Exception as e:
        print(f"\n❌ BACKUP FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

