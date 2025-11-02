# rag_service.py
# ClauseBot RAG Service: Embedding generation, retrieval, and LLM response generation
from __future__ import annotations

import os
import asyncio
from typing import List, Optional, Dict
from dataclasses import dataclass
import tiktoken
from openai import AsyncOpenAI
from supabase import create_client, Client

# Environment configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set - RAG service cannot initialize")
if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set")

# Initialize clients
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Token encoding for cost/usage tracking
encoding = tiktoken.get_encoding("cl100k_base")

@dataclass
class RetrievedClause:
    """Represents a clause retrieved from the vector database"""
    clause_id: str
    standard: str
    section: str
    title: str
    content: str
    similarity: float
    rank: float

    def citation_text(self) -> str:
        """Format citation for LLM response"""
        return f"[{self.standard} {self.section}]"

# System prompt: strict grounding rules
COMPLIANCE_SYSTEM_PROMPT = """You are ClauseBot, a Compliance Research Analyst specializing in welding and NDT standards.

STRICT RULES:
1. Answer ONLY using the provided retrieved clauses below.
2. Cite every factual claim using the format [Standard Section], e.g., [AWS D1.1:2020 4.8.3].
3. If the retrieved clauses don't contain sufficient information, reply: "I don't have sufficient information in the retrieved standards to answer this fully."
4. Do NOT hallucinate. Do NOT provide opinions. Quote ambiguous text verbatim.
5. If multiple clauses conflict, show both and cite them.

RETRIEVED CLAUSES:
{retrieved_context}

USER QUERY:
{user_query}

Answer (with citations):"""

async def generate_query_embedding(query: str) -> List[float]:
    """
    Generate embedding vector for a user query using OpenAI text-embedding-3-large.
    
    Args:
        query: User's compliance question
        
    Returns:
        3072-dimensional embedding vector
    """
    try:
        resp = await openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=query
        )
        return resp.data[0].embedding
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        raise

def retrieve_relevant_clauses(
    query_embedding: List[float],
    query_text: str,
    standard: Optional[str] = None,
    top_k: int = 5,
    threshold: float = 0.60
) -> List[RetrievedClause]:
    """
    Retrieve relevant clauses using hybrid search (semantic + full-text).
    
    Args:
        query_embedding: 3072-dim vector from generate_query_embedding
        query_text: Original query text for full-text search
        standard: Optional filter (e.g., "AWS D1.1:2020")
        top_k: Number of results to return
        threshold: Minimum similarity score (0.0-1.0)
        
    Returns:
        List of RetrievedClause objects
    """
    try:
        result = supabase.rpc(
            'search_clauses_hybrid',
            {
                'query_embedding': query_embedding,
                'query_text': query_text,
                'match_threshold': threshold,
                'match_count': top_k,
                'filter_standard': standard
            }
        ).execute()
        
        rows = result.data or []
        clauses = []
        
        for r in rows:
            clauses.append(RetrievedClause(
                clause_id=r['clause_id'],
                standard=r['standard'],
                section=r['section'],
                title=r['title'],
                content=r['content'],
                similarity=float(r.get('similarity', 0.0)),
                rank=float(r.get('rank', 0.0))
            ))
        
        return clauses
    except Exception as e:
        print(f"Error retrieving clauses: {e}")
        return []

async def generate_rag_response(
    query: str,
    retrieved_clauses: List[RetrievedClause],
    session_id: str,
    model: str = "gpt-4o",
    temperature: float = 0.0
) -> Dict:
    """
    Generate LLM response grounded in retrieved clauses and log citations.
    
    Args:
        query: User's original query
        retrieved_clauses: Clauses from retrieve_relevant_clauses
        session_id: Session identifier for citation logging
        model: OpenAI model name
        temperature: LLM temperature (0.0 = deterministic)
        
    Returns:
        Dict with 'answer', 'citations', and 'metadata'
    """
    # Build retrieved context
    context_parts = []
    for idx, c in enumerate(retrieved_clauses, start=1):
        context_parts.append(
            f"=== CLAUSE {idx}: {c.standard} {c.section} - {c.title} ===\n"
            f"{c.content}\n"
            f"(Relevance: {c.similarity:.3f})\n"
        )
    retrieved_context = "\n".join(context_parts)
    
    # Build prompt
    prompt = COMPLIANCE_SYSTEM_PROMPT.format(
        retrieved_context=retrieved_context,
        user_query=query
    )
    
    # Token counting (approximate)
    prompt_tokens = len(encoding.encode(prompt))
    
    # Call OpenAI Chat Completion
    try:
        completion = await openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": prompt}],
            temperature=temperature,
            max_tokens=1500
        )
        answer = completion.choices[0].message.content
        completion_tokens = completion.usage.completion_tokens if completion.usage else 0
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        raise
    
    # Log citations to Supabase (best-effort, don't fail request)
    for c in retrieved_clauses:
        try:
            supabase.table('chat_citations').insert({
                'session_id': session_id,
                'query': query,
                'clause_id': c.clause_id,
                'similarity_score': c.similarity,
                'used_in_response': True
            }).execute()
        except Exception as e:
            print(f"Warning: Failed to log citation for {c.clause_id}: {e}")
    
    return {
        'answer': answer,
        'citations': [
            {
                'clause_id': c.clause_id,
                'standard': c.standard,
                'section': c.section,
                'title': c.title,
                'similarity': c.similarity,
                'citation_text': c.citation_text()
            }
            for c in retrieved_clauses
        ],
        'metadata': {
            'model': model,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'retrieval_count': len(retrieved_clauses)
        }
    }

async def rag_pipeline(
    query: str,
    session_id: str,
    standard: Optional[str] = None,
    top_k: int = 5
) -> Dict:
    """
    Full RAG pipeline: embed → retrieve → generate → log.
    
    Args:
        query: User's compliance question
        session_id: Session identifier
        standard: Optional filter (e.g., "AWS D1.1:2020")
        top_k: Number of clauses to retrieve
        
    Returns:
        Dict with 'answer', 'citations', 'metadata'
    """
    # Step 1: Generate query embedding
    query_embedding = await generate_query_embedding(query)
    
    # Step 2: Retrieve relevant clauses
    clauses = retrieve_relevant_clauses(
        query_embedding=query_embedding,
        query_text=query,
        standard=standard,
        top_k=top_k
    )
    
    # Step 3: Handle no results
    if not clauses:
        return {
            'answer': "I couldn't find relevant clauses in the knowledge base to answer your question. Try rephrasing or consult the standard directly.",
            'citations': [],
            'metadata': {'retrieval_count': 0}
        }
    
    # Step 4: Generate response and log
    response = await generate_rag_response(
        query=query,
        retrieved_clauses=clauses,
        session_id=session_id
    )
    
    return response

