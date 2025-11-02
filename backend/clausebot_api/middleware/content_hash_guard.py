# content_hash_guard.py
# Middleware to enforce content integrity for NotebookLM SSOT
# Validates SHA-256 hash of content before allowing ingestion/updates

import hashlib
import json
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

class ContentHashGuardMiddleware(BaseHTTPMiddleware):
    """
    Validates content_hash for POST/PUT requests to SSOT endpoints
    
    Blocks ingestion if:
    - content_hash missing
    - computed hash doesn't match provided hash
    - cms_tag not set to 'source: notebooklm'
    
    Logs violations to clause_sme_log for SME review
    """
    
    def __init__(self, app, supabase_client=None, enabled: bool = True):
        super().__init__(app)
        self.supabase = supabase_client
        self.enabled = enabled
        self.protected_paths = [
            "/v1/ssot/clauses",
            "/v1/content/ingest",
            "/v1/sme/submit"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip if middleware disabled or not a protected endpoint
        if not self.enabled or request.method.upper() not in ["POST", "PUT"]:
            return await call_next(request)
        
        path = request.url.path
        if not any(path.startswith(protected) for protected in self.protected_paths):
            return await call_next(request)
        
        # Read and validate request body
        try:
            body_bytes = await request.body()
            body = json.loads(body_bytes) if body_bytes else {}
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON in request body"
            )
        
        # Extract required fields
        content = body.get("content")
        content_hash = body.get("content_hash")
        cms_tag = body.get("cms_tag")
        canonical_id = body.get("canonical_id") or body.get("clause_id")
        
        # Validate required fields present
        if not content:
            raise HTTPException(
                status_code=400,
                detail="content is required for SSOT ingestion"
            )
        
        if not content_hash:
            raise HTTPException(
                status_code=400,
                detail="content_hash is required for integrity verification"
            )
        
        if not cms_tag or cms_tag != "source: notebooklm":
            raise HTTPException(
                status_code=400,
                detail="cms_tag must be 'source: notebooklm' for SSOT compliance"
            )
        
        # Compute SHA-256 hash of content
        computed_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        
        # Validate hash matches
        if computed_hash != content_hash:
            # Log mismatch for SME review
            if self.supabase:
                try:
                    self.supabase.table('clause_sme_log').insert({
                        'canonical_id': canonical_id,
                        'sme_user': 'system',
                        'action': 'rejected',
                        'action_note': f'Content hash mismatch: computed={computed_hash[:16]}..., provided={content_hash[:16]}...',
                        'action_payload': {
                            'path': path,
                            'method': request.method,
                            'computed_hash': computed_hash,
                            'provided_hash': content_hash
                        },
                        'priority': 'P1'
                    }).execute()
                except Exception as e:
                    print(f"[ContentHashGuard] Failed to log violation: {e}")
            
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "content_hash_mismatch",
                    "message": "Content integrity check failed. Ingestion blocked.",
                    "computed_hash": computed_hash[:16] + "...",
                    "provided_hash": content_hash[:16] + "...",
                    "action_required": "Review content for unauthorized modifications"
                }
            )
        
        # Hash valid - recreate request with validated body for downstream processing
        async def receive():
            return {"type": "http.request", "body": body_bytes}
        
        request._receive = receive
        
        # Log successful validation (optional, for audit trail)
        if self.supabase and canonical_id:
            try:
                self.supabase.table('clause_sme_log').insert({
                    'canonical_id': canonical_id,
                    'sme_user': body.get('sme_reviewer_initials', 'unknown'),
                    'action': 'submitted',
                    'action_note': 'Content hash validated successfully',
                    'action_payload': {
                        'path': path,
                        'content_hash': content_hash,
                        'nlm_source_id': body.get('nlm_source_id')
                    },
                    'priority': 'P2'
                }).execute()
            except Exception as e:
                # Don't block request on logging failure
                print(f"[ContentHashGuard] Failed to log validation: {e}")
        
        return await call_next(request)

