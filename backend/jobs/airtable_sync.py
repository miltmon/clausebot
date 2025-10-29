"""
ClauseBot Airtable → Supabase Sync Job
Runs nightly via Render cron to keep Supabase in sync with Airtable

Schedule: 09:00 UTC (01:00 PT / 02:00 PDT) via render.yaml
Purpose: Pull quiz questions, clauses, editions from Airtable → upsert to Supabase

Usage:
    python -m jobs.airtable_sync
"""
import os
import sys
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from pyairtable import Api
from supabase import create_client, Client
from redis.asyncio import Redis


def get_supabase() -> Client:
    """Create Supabase client with service role key."""
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_KEY"]
    return create_client(url, key)


def get_airtable_api() -> Api:
    """Create Airtable API client."""
    token = os.environ.get("AIRTABLE_PAT") or os.environ.get("AIRTABLE_API_KEY")
    if not token:
        raise ValueError("AIRTABLE_PAT or AIRTABLE_API_KEY required")
    return Api(token)


def normalize_quiz_record(record: dict) -> dict:
    """
    Transform Airtable record to Supabase quiz_items schema.
    
    Airtable fields:
        - Question (text)
        - Choices (text, newline-separated)
        - Answer (text)
        - Clause (text, e.g., "4.1.2")
        - Difficulty (text: Easy/Medium/Hard)
        - SourceRef (text, e.g., "AWS D1.1:2025")
        - UpdatedAt (datetime)
    
    Supabase schema:
        - id (text, from Airtable ID)
        - clause (text)
        - question (text)
        - choices (text[])
        - answer (text)
        - difficulty (text)
        - source_ref (text)
        - updated_at (timestamp)
        - synced_at (timestamp, set on insert)
    """
    fields = record.get("fields", {})
    
    # Parse choices (newline-separated string → array)
    choices_raw = fields.get("Choices", "")
    choices = [c.strip() for c in choices_raw.split("\n") if c.strip()]
    
    return {
        "id": record["id"],
        "clause": fields.get("Clause"),
        "question": fields.get("Question"),
        "choices": choices,
        "answer": fields.get("Answer"),
        "difficulty": fields.get("Difficulty", "Medium"),
        "source_ref": fields.get("SourceRef", "AWS D1.1:2025"),
        "updated_at": fields.get("UpdatedAt"),
        "synced_at": datetime.utcnow().isoformat(),
    }


def normalize_clause_record(record: dict) -> dict:
    """
    Transform Airtable clause to Supabase clauses schema.
    
    Airtable fields:
        - ClauseNum (text, e.g., "4.1.2")
        - Title (text)
        - Content (text, long)
        - Edition (text, e.g., "AWS D1.1:2025")
        - Section (text, e.g., "Part A - General Requirements")
    
    Supabase schema:
        - id (generated)
        - clause_num (text)
        - title (text)
        - content (text)
        - edition (text)
        - section (text)
        - synced_at (timestamp)
    """
    fields = record.get("fields", {})
    
    return {
        "id": record["id"],
        "clause_num": fields.get("ClauseNum"),
        "title": fields.get("Title"),
        "content": fields.get("Content"),
        "edition": fields.get("Edition", "AWS D1.1:2025"),
        "section": fields.get("Section"),
        "synced_at": datetime.utcnow().isoformat(),
    }


async def fetch_airtable_table(
    api: Api,
    base_id: str,
    table_name: str,
    view_name: Optional[str] = None
) -> List[dict]:
    """Fetch all records from an Airtable table."""
    print(f"📥 Fetching Airtable: {table_name} (view: {view_name or 'default'})")
    
    table = api.table(base_id, table_name)
    
    if view_name:
        records = table.all(view=view_name)
    else:
        records = table.all()
    
    print(f"   ✅ Fetched {len(records)} records")
    return records


async def upsert_to_supabase(
    sb: Client,
    table_name: str,
    records: List[dict]
) -> dict:
    """
    Upsert records to Supabase table.
    
    Args:
        sb: Supabase client
        table_name: Target table name
        records: List of normalized records
    
    Returns:
        Dict with count, errors
    """
    if not records:
        print(f"⏭️  No records to upsert for {table_name}")
        return {"count": 0, "errors": []}
    
    print(f"📤 Upserting {len(records)} records to Supabase: {table_name}")
    
    try:
        # Upsert in batches of 100 (Supabase limit)
        batch_size = 100
        total = 0
        errors = []
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            try:
                result = sb.table(table_name).upsert(batch, on_conflict="id").execute()
                total += len(batch)
                print(f"   ✅ Batch {i//batch_size + 1}: {len(batch)} records")
            except Exception as e:
                error_msg = f"Batch {i//batch_size + 1} failed: {e}"
                print(f"   ❌ {error_msg}")
                errors.append(error_msg)
        
        print(f"   ✅ Total upserted: {total}/{len(records)}")
        return {"count": total, "errors": errors}
    
    except Exception as e:
        print(f"❌ Upsert failed: {e}")
        return {"count": 0, "errors": [str(e)]}


async def warm_cache():
    """
    Clear cache after sync to force fresh data.
    Deletes all keys matching "cb:/v1/quiz*" and "cb:/v1/clause*"
    """
    kv_url = os.getenv("KV_URL")
    if not kv_url:
        print("⏭️  KV_URL not set - skipping cache warm")
        return
    
    print("🔥 Warming cache (clearing stale keys)")
    
    try:
        redis = Redis.from_url(kv_url, decode_responses=True)
        
        patterns = ["cb:/v1/quiz*", "cb:/v1/clause*", "cb:/v1/search*"]
        total = 0
        
        for pattern in patterns:
            count = 0
            async for key in redis.scan_iter(match=pattern):
                await redis.delete(key)
                count += 1
            total += count
            if count > 0:
                print(f"   ✅ Cleared {count} keys matching {pattern}")
        
        print(f"   ✅ Total keys cleared: {total}")
        await redis.close()
    
    except Exception as e:
        print(f"⚠️  Cache warm failed (non-fatal): {e}")


async def sync_quiz_items():
    """Sync quiz questions from Airtable to Supabase."""
    print("\n" + "="*60)
    print("🔄 QUIZ ITEMS SYNC")
    print("="*60)
    
    api = get_airtable_api()
    sb = get_supabase()
    
    base_id = os.environ["AIRTABLE_BASE_ID"]
    table_name = os.environ.get("AIRTABLE_CLAUSES_TABLE", "tblvvclz8NSpiSVR9")
    view_name = os.environ.get("AIRTABLE_VIEW")
    
    # Fetch from Airtable
    records = await fetch_airtable_table(api, base_id, table_name, view_name)
    
    # Normalize
    normalized = [normalize_quiz_record(r) for r in records]
    
    # Upsert to Supabase
    result = await upsert_to_supabase(sb, "quiz_items", normalized)
    
    return result


async def sync_clauses():
    """Sync clauses from Airtable to Supabase."""
    print("\n" + "="*60)
    print("🔄 CLAUSES SYNC")
    print("="*60)
    
    # Check if clauses table is configured
    clauses_table = os.environ.get("AIRTABLE_CLAUSES_TABLE")
    if not clauses_table:
        print("⏭️  AIRTABLE_CLAUSES_TABLE not set - skipping")
        return {"count": 0, "errors": []}
    
    api = get_airtable_api()
    sb = get_supabase()
    
    base_id = os.environ["AIRTABLE_BASE_ID"]
    
    # Fetch from Airtable
    records = await fetch_airtable_table(api, base_id, clauses_table)
    
    # Normalize
    normalized = [normalize_clause_record(r) for r in records]
    
    # Upsert to Supabase
    result = await upsert_to_supabase(sb, "clauses", normalized)
    
    return result


async def main():
    """Main sync routine."""
    print("🚀 ClauseBot Airtable → Supabase Sync")
    print(f"⏰ Started at: {datetime.utcnow().isoformat()}")
    
    sync_mode = os.getenv("SYNC_MODE", "full")
    print(f"🎯 Mode: {sync_mode}")
    
    results = {}
    
    try:
        # Sync quiz items (always)
        results["quiz_items"] = await sync_quiz_items()
        
        # Sync clauses (optional, depends on config)
        if sync_mode in ("full", "clauses"):
            results["clauses"] = await sync_clauses()
        
        # Warm cache
        await warm_cache()
        
        # Summary
        print("\n" + "="*60)
        print("✅ SYNC COMPLETE")
        print("="*60)
        for table, result in results.items():
            print(f"  {table}: {result['count']} records")
            if result["errors"]:
                print(f"    ⚠️  {len(result['errors'])} errors")
        
        print(f"⏰ Finished at: {datetime.utcnow().isoformat()}")
        
        # Exit with error code if any errors
        total_errors = sum(len(r["errors"]) for r in results.values())
        if total_errors > 0:
            print(f"\n⚠️  Completed with {total_errors} errors")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ SYNC FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

