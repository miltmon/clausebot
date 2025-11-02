# ingest_aws_d11.py
# One-shot ingestion script for AWS D1.1 clauses
# Reads JSON, generates embeddings, upserts to Supabase
import os
import asyncio
import json
from pathlib import Path
from openai import AsyncOpenAI
from supabase import create_client

# Environment configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not (OPENAI_API_KEY and SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY):
    raise RuntimeError("Missing required env vars: OPENAI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY")

# Initialize clients
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Path to clauses JSON (adjust if your structure differs)
DATA_JSON = Path(__file__).parent.parent / "data" / "codes" / "aws_d1_1_2020" / "index" / "clauses.json"

async def generate_embeddings(texts: list) -> list:
    """
    Generate embeddings for a batch of texts using OpenAI text-embedding-3-large.
    
    Args:
        texts: List of strings to embed
        
    Returns:
        List of 3072-dimensional embedding vectors
    """
    try:
        resp = await openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=texts
        )
        return [d.embedding for d in resp.data]
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        raise

def extract_keywords(text: str) -> list:
    """
    Extract common welding/compliance keywords from text.
    
    Simple keyword matching; enhance with NLP for production.
    """
    common_terms = [
        'weld', 'welding', 'preheat', 'wps', 'pqr', 'cwi', 
        'inspection', 'examination', 'procedure', 'joint', 
        'fillet', 'root', 'base metal', 'qualification',
        'electrode', 'interpass', 'undercut', 'reinforcement'
    ]
    text_lower = (text or "").lower()
    return [term for term in common_terms if term in text_lower]

async def main():
    """
    Main ingestion workflow:
    1. Load clauses.json
    2. Prepare metadata for each clause
    3. Generate embeddings in batches
    4. Upsert to Supabase
    """
    # Check that data file exists
    if not DATA_JSON.exists():
        raise FileNotFoundError(
            f"Data file not found: {DATA_JSON}\n"
            f"Expected format: backend/data/codes/aws_d1_1_2020/index/clauses.json"
        )
    
    print(f"Loading clauses from {DATA_JSON}...")
    with open(DATA_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract clauses (adjust based on your JSON structure)
    clauses = data.get('clauses', {})
    if not clauses:
        raise ValueError("No 'clauses' key found in JSON or clauses dict is empty")
    
    print(f"Found {len(clauses)} clauses to ingest")
    
    # Prepare content and metadata
    texts = []
    metadata_rows = []
    
    for clause_id, clause_data in clauses.items():
        title = clause_data.get('title', '')
        summary = clause_data.get('summary', '') or clause_data.get('content', '')
        content = f"{title}\n\n{summary}"
        
        texts.append(content)
        metadata_rows.append({
            'clause_id': f"aws_d1.1_2020_{clause_id}",
            'standard': 'AWS D1.1:2020',
            'section': clause_id,
            'parent_section': clause_id.rsplit('.', 1)[0] if '.' in clause_id else clause_id,
            'title': title,
            'content': content,
            'chunk_type': 'paragraph',
            'effective_date': '2020-11-01',
            'page_number': clause_data.get('page'),
            'keywords': extract_keywords(title + ' ' + summary)
        })
    
    # Generate embeddings in batches (OpenAI rate limit: 3,000 RPM for tier 1)
    BATCH_SIZE = 50
    embeddings = []
    
    print(f"Generating embeddings in batches of {BATCH_SIZE}...")
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i+BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE
        
        print(f"  Batch {batch_num}/{total_batches}: Embedding {len(batch_texts)} clauses...")
        batch_embeddings = await generate_embeddings(batch_texts)
        embeddings.extend(batch_embeddings)
        
        # Small delay to respect rate limits
        if i + BATCH_SIZE < len(texts):
            await asyncio.sleep(0.5)
    
    print(f"Generated {len(embeddings)} embeddings")
    
    # Upsert to Supabase
    print("Upserting to Supabase...")
    success_count = 0
    error_count = 0
    
    for meta, emb in zip(metadata_rows, embeddings):
        meta['embedding'] = emb
        try:
            supabase.table('clause_embeddings').upsert(
                meta,
                on_conflict='clause_id'
            ).execute()
            success_count += 1
        except Exception as e:
            error_count += 1
            print(f"  Error upserting {meta.get('clause_id')}: {e}")
    
    print("\n" + "="*60)
    print("INGESTION COMPLETE")
    print("="*60)
    print(f"Total clauses processed: {len(metadata_rows)}")
    print(f"Successfully upserted: {success_count}")
    print(f"Errors: {error_count}")
    print("="*60)
    
    # Verification query
    try:
        result = supabase.table('clause_embeddings').select('standard', count='exact').execute()
        print(f"\nVerification: {result.count} total clauses in database")
    except Exception as e:
        print(f"Verification query failed: {e}")

if __name__ == "__main__":
    print("="*60)
    print("ClauseBot RAG - AWS D1.1 Ingestion")
    print("="*60)
    asyncio.run(main())

