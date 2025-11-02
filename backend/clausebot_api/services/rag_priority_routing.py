# rag_priority_routing.py
# Phase 3: ClauseBot Priority Routing with NLM SSOT Integration
# Implements 3-tier priority system: Exact NLM match → Clause match → Generic NLP

from __future__ import annotations
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from supabase import Client

@dataclass
class NLMMetadata:
    """NotebookLM SSOT metadata for content validation"""
    nlm_source_id: str
    nlm_timestamp: datetime
    code_reference_primary: str
    sme_reviewer_initials: str
    cms_tag: str
    content_hash: str

@dataclass
class PriorityMatch:
    """Result of priority routing with match reason"""
    priority_level: int  # 1 (exact), 2 (clause), 3 (generic)
    match_reason: str
    clause_id: str
    nlm_metadata: Optional[NLMMetadata]
    similarity: float
    content: str

class MiltmonNDTLogger:
    """Logs fallback queries to 'MiltmonNDT Q Upload Log' for SME review"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    def log_fallback_query(
        self,
        query: str,
        session_id: str,
        retrieved_clauses: List[Dict],
        reason: str = "no_priority_match"
    ):
        """
        Log queries that fell back to generic NLP (Priority 3)
        
        Args:
            query: User's original query
            session_id: Session identifier
            retrieved_clauses: Clauses returned by generic retrieval
            reason: Why priority routing failed
        """
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'query': query,
                'session_id': session_id,
                'fallback_reason': reason,
                'retrieved_clause_ids': [c.get('clause_id') for c in retrieved_clauses],
                'sme_action_required': True,
                'suggested_question_range': 'Q051-Q110',
                'priority': 'high' if 'ASME' in query or 'AWS D1.1' in query else 'medium'
            }
            
            # Log to dedicated Supabase table
            self.supabase.table('miltmon_ndt_q_upload_log').insert(log_entry).execute()
            print(f"[MiltmonNDT Log] Logged fallback query: {query[:50]}...")
            
        except Exception as e:
            print(f"[MiltmonNDT Log] Error logging fallback: {e}")

class PriorityRouter:
    """
    Implements 3-tier priority routing for ClauseBot retrieval
    
    Priority 1: Exact NLM ID + Clause match
    Priority 2: Clause + Keyword match
    Priority 3: Generic NLP (with fallback logging)
    """
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.logger = MiltmonNDTLogger(supabase)
        
        # Regex patterns for detection
        self.nlm_id_pattern = re.compile(r'(NLM-[A-Z0-9-]+|Q\d{3,4})', re.IGNORECASE)
        self.clause_pattern = re.compile(
            r'(AWS D1\.1:?\s*\d{4}?\s*)?'
            r'(Clause|Section|Table|Figure|Annex)?\s*'
            r'(\d+\.?\d*\.?\d*\.?\d*)',
            re.IGNORECASE
        )
        self.asme_pattern = re.compile(
            r'ASME\s+(Section\s+)?([IVX]+)\s+(QW-\d+\.?\d*)',
            re.IGNORECASE
        )
    
    def extract_query_metadata(self, query: str) -> Dict:
        """
        Extract NLM IDs and clause references from query
        
        Returns:
            Dict with 'nlm_ids', 'clauses', 'asme_refs', 'keywords'
        """
        nlm_ids = self.nlm_id_pattern.findall(query)
        clauses = self.clause_pattern.findall(query)
        asme_refs = self.asme_pattern.findall(query)
        
        # Extract critical keywords
        keywords = []
        critical_terms = [
            'preheat', 'wps', 'pqr', 'essential variable',
            'qualification', 'inspection', 'acceptance criteria',
            'PAUT', 'RT-D', 'digital radiography', 'CVN'
        ]
        query_lower = query.lower()
        keywords = [term for term in critical_terms if term.lower() in query_lower]
        
        return {
            'nlm_ids': nlm_ids,
            'clauses': clauses,
            'asme_refs': asme_refs,
            'keywords': keywords
        }
    
    def priority_1_match(
        self,
        query: str,
        query_metadata: Dict
    ) -> Optional[PriorityMatch]:
        """
        Priority 1: Exact NLM ID + Clause match
        
        Example: "Q032 acceptance criteria AWS D1.1 8.15"
        """
        if not query_metadata['nlm_ids'] or not (query_metadata['clauses'] or query_metadata['asme_refs']):
            return None
        
        nlm_id = query_metadata['nlm_ids'][0]
        clause = query_metadata['clauses'][0][2] if query_metadata['clauses'] else None
        
        try:
            # Query clause_embeddings for exact NLM + Clause match
            result = self.supabase.table('clause_embeddings').select(
                'clause_id, content, nlm_source_id, nlm_timestamp, '
                'code_reference_primary, sme_reviewer_initials, cms_tag, content_hash'
            ).eq('nlm_source_id', nlm_id).eq('section', clause).execute()
            
            if result.data and len(result.data) > 0:
                row = result.data[0]
                
                # Verify CMS tag compliance
                if row.get('cms_tag') != 'source: notebooklm':
                    print(f"[Priority 1] WARNING: Non-NLM content found for {nlm_id}")
                    return None
                
                nlm_meta = NLMMetadata(
                    nlm_source_id=row['nlm_source_id'],
                    nlm_timestamp=datetime.fromisoformat(row['nlm_timestamp']),
                    code_reference_primary=row['code_reference_primary'],
                    sme_reviewer_initials=row['sme_reviewer_initials'],
                    cms_tag=row['cms_tag'],
                    content_hash=row.get('content_hash', '')
                )
                
                return PriorityMatch(
                    priority_level=1,
                    match_reason=f"Exact NLM ID ({nlm_id}) + Clause ({clause}) match",
                    clause_id=row['clause_id'],
                    nlm_metadata=nlm_meta,
                    similarity=1.0,  # Exact match
                    content=row['content']
                )
        except Exception as e:
            print(f"[Priority 1] Error: {e}")
        
        return None
    
    def priority_2_match(
        self,
        query: str,
        query_metadata: Dict
    ) -> Optional[PriorityMatch]:
        """
        Priority 2: Clause + Keyword match
        
        Example: "ASME Section IX QW-200.1 WPS purpose"
        """
        clauses = query_metadata['clauses']
        asme_refs = query_metadata['asme_refs']
        keywords = query_metadata['keywords']
        
        if not (clauses or asme_refs) or not keywords:
            return None
        
        # Build clause reference
        if asme_refs:
            clause_ref = f"ASME {asme_refs[0][1]} {asme_refs[0][2]}"
        elif clauses:
            clause_ref = clauses[0][2]
        else:
            return None
        
        try:
            # Query for clause + keyword match with NLM tag filter
            query_builder = self.supabase.table('clause_embeddings').select(
                'clause_id, content, nlm_source_id, nlm_timestamp, '
                'code_reference_primary, sme_reviewer_initials, cms_tag, content_hash'
            ).eq('cms_tag', 'source: notebooklm')
            
            # Match clause reference
            if 'ASME' in clause_ref:
                query_builder = query_builder.ilike('code_reference_primary', f'%{clause_ref}%')
            else:
                query_builder = query_builder.eq('section', clause_ref)
            
            result = query_builder.limit(5).execute()
            
            if result.data and len(result.data) > 0:
                # Rank by keyword presence in content
                best_match = None
                best_score = 0
                
                for row in result.data:
                    content_lower = row['content'].lower()
                    keyword_score = sum(1 for kw in keywords if kw.lower() in content_lower)
                    
                    if keyword_score > best_score:
                        best_score = keyword_score
                        best_match = row
                
                if best_match:
                    nlm_meta = NLMMetadata(
                        nlm_source_id=best_match['nlm_source_id'],
                        nlm_timestamp=datetime.fromisoformat(best_match['nlm_timestamp']),
                        code_reference_primary=best_match['code_reference_primary'],
                        sme_reviewer_initials=best_match['sme_reviewer_initials'],
                        cms_tag=best_match['cms_tag'],
                        content_hash=best_match.get('content_hash', '')
                    )
                    
                    return PriorityMatch(
                        priority_level=2,
                        match_reason=f"Clause ({clause_ref}) + Keywords ({', '.join(keywords)}) match",
                        clause_id=best_match['clause_id'],
                        nlm_metadata=nlm_meta,
                        similarity=0.85 + (best_score * 0.05),  # Boost for keyword matches
                        content=best_match['content']
                    )
        except Exception as e:
            print(f"[Priority 2] Error: {e}")
        
        return None
    
    def route_query(
        self,
        query: str,
        session_id: str,
        generic_retrieval_callback
    ) -> Tuple[PriorityMatch, List[Dict]]:
        """
        Main routing logic: Try Priority 1 → Priority 2 → Priority 3 (generic)
        
        Args:
            query: User query
            session_id: Session ID for logging
            generic_retrieval_callback: Function to call for Priority 3 generic retrieval
            
        Returns:
            Tuple of (best_match, all_retrieved_clauses)
        """
        # Extract metadata from query
        query_metadata = self.extract_query_metadata(query)
        
        print(f"[Priority Router] Query metadata: {query_metadata}")
        
        # Try Priority 1: Exact NLM ID + Clause
        p1_match = self.priority_1_match(query, query_metadata)
        if p1_match:
            print(f"[Priority Router] ✅ Priority 1 match: {p1_match.match_reason}")
            return p1_match, [{'clause_id': p1_match.clause_id, 'content': p1_match.content}]
        
        # Try Priority 2: Clause + Keyword
        p2_match = self.priority_2_match(query, query_metadata)
        if p2_match:
            print(f"[Priority Router] ✅ Priority 2 match: {p2_match.match_reason}")
            return p2_match, [{'clause_id': p2_match.clause_id, 'content': p2_match.content}]
        
        # Fallback to Priority 3: Generic NLP retrieval
        print(f"[Priority Router] ⚠️ Falling back to Priority 3 (generic NLP)")
        
        # Call generic retrieval (existing RAG service)
        generic_results = generic_retrieval_callback(query)
        
        # Log fallback for SME review
        self.logger.log_fallback_query(
            query=query,
            session_id=session_id,
            retrieved_clauses=generic_results,
            reason="no_nlm_metadata_or_clause_match"
        )
        
        # Create Priority 3 match from best generic result
        if generic_results:
            best_result = generic_results[0]
            p3_match = PriorityMatch(
                priority_level=3,
                match_reason="Generic NLP fallback (logged for SME review)",
                clause_id=best_result.get('clause_id', ''),
                nlm_metadata=None,  # No NLM metadata for generic results
                similarity=best_result.get('similarity', 0.0),
                content=best_result.get('content', '')
            )
            return p3_match, generic_results
        
        # No results at any priority level
        return None, []

