#!/usr/bin/env python3
"""
Welding Resources Data Ingestion Script
Ingests CSV files into welding_resources table

Usage:
    python backend/scripts/ingest_welding_data.py
    
Environment variables required:
    SUPABASE_URL
    SUPABASE_SERVICE_ROLE_KEY
"""
import os
import sys
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from supabase import create_client, Client

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def get_supabase_client() -> Client:
    """Initialize Supabase client"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
    
    return create_client(url, key)

def parse_csv_row(row: Dict[str, str], category: str) -> Dict:
    """Parse CSV row into database record"""
    # Parse published date
    published_date = None
    if row.get("Published Date"):
        try:
            published_date = datetime.fromisoformat(row["Published Date"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            pass
    
    return {
        "url": row.get("URL", "").strip(),
        "title": row.get("Title", "").strip(),
        "description": row.get("Description", "").strip() or None,
        "author": row.get("Author", "").strip() or None,
        "published_date": published_date.isoformat() if published_date else None,
        "category": category,
        "summary": row.get("Article Summary (Result)", "").strip() or None
    }

def ingest_csv_file(supabase: Client, file_path: Path, category: str) -> int:
    """
    Ingest a CSV file into the database
    
    Args:
        supabase: Supabase client
        file_path: Path to CSV file
        category: Category for resources (welding_symbols or cwi_resources)
    
    Returns:
        Number of records ingested
    """
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return 0
    
    print(f"📖 Reading {file_path.name}...")
    
    records = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("URL"):
                continue
            
            record = parse_csv_row(row, category)
            if record["url"] and record["title"]:
                records.append(record)
    
    print(f"   Found {len(records)} valid records")
    
    if not records:
        print("   ⚠️  No valid records to insert")
        return 0
    
    # Insert records (upsert on URL conflict)
    print(f"💾 Inserting into database...")
    
    try:
        response = supabase.table("welding_resources")\
            .upsert(records, on_conflict="url")\
            .execute()
        
        inserted_count = len(response.data) if response.data else 0
        print(f"   ✅ Inserted/updated {inserted_count} records")
        return inserted_count
    
    except Exception as e:
        print(f"   ❌ Error inserting records: {e}")
        return 0

def main():
    """Main ingestion process"""
    print("=" * 60)
    print("WELDING RESOURCES DATA INGESTION")
    print("=" * 60)
    print()
    
    # Initialize Supabase client
    print("🔌 Connecting to Supabase...")
    try:
        supabase = get_supabase_client()
        print("   ✅ Connected")
    except ValueError as e:
        print(f"   ❌ {e}")
        sys.exit(1)
    print()
    
    # Define CSV files and their categories
    data_dir = Path(__file__).parent.parent / "data"
    files = [
        (data_dir / "webset-articles_weld_and_welding_symbols.csv", "welding_symbols"),
        (data_dir / "webset-articles_asme_aws_cwi_welding_resources.csv", "cwi_resources")
    ]
    
    total_ingested = 0
    
    # Ingest each file
    for file_path, category in files:
        count = ingest_csv_file(supabase, file_path, category)
        total_ingested += count
        print()
    
    # Print summary
    print("=" * 60)
    print(f"✅ INGESTION COMPLETE: {total_ingested} total records")
    print("=" * 60)
    print()
    
    # Verify data
    print("🔍 Verifying data in database...")
    try:
        symbols_count = supabase.table("welding_resources")\
            .select("id", count="exact")\
            .eq("category", "welding_symbols")\
            .execute()
        
        cwi_count = supabase.table("welding_resources")\
            .select("id", count="exact")\
            .eq("category", "cwi_resources")\
            .execute()
        
        print(f"   Welding Symbols: {symbols_count.count or 0} articles")
        print(f"   CWI Resources: {cwi_count.count or 0} articles")
        print(f"   Total: {(symbols_count.count or 0) + (cwi_count.count or 0)} articles")
        print()
        print("✅ Verification complete!")
    except Exception as e:
        print(f"   ⚠️  Verification failed: {e}")

if __name__ == "__main__":
    main()

