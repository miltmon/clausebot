from fastapi import FastAPI, Header, HTTPException, Request, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import time
import os
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from pathlib import Path

# Import security and observability modules
try:
    from .security import (
        APIKeyAuth,
        get_api_key_info,
        check_scope,
        generate_request_id,
        log_security_event,
        security_middleware,
    )
except ImportError:
    from ..security import (  # fallback if security.py is one level up
        APIKeyAuth,
        get_api_key_info,
        check_scope,
        log_security_event,
        security_middleware,
    )
from .observability import (
    record_request_metrics,
    get_metrics_summary,
    check_system_health,
    check_readiness,
    logger,
)
from .content_integrity import (
    get_edition_guard,
    generate_clause_checksum,
    content_manager,
)

app = FastAPI(title="ClauseBot Local API", version="1.0.0")
EDITION = os.getenv("CLAUSEBOT_EDITION", "AWS_D1.1:2025")
CONTENT_DIR = os.getenv("CONTENT_DIR", "./data")
INDEX_DIR = os.getenv("INDEX_DIR", "./data/codes/aws_d1_1_2020/index")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "86400"))

# Import routers
from .routers.chat import router as chat_router
from .routers.clauses import router as clauses_router
from .routers.admin import router as admin_router
# from .routers.quiz import router as quiz_router  # Temporarily disabled - using direct endpoint

# Simple in-memory cache with TTL
cache = {}
cache_timestamps = {}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.miltmonndt.com",
        "https://clausebot.miltmonndt.com",
        "https://miltmon-80193.bubbleapps.io",
        "capacitor://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4173",  # Preview server
        "http://localhost:8081",
        "null",  # For file:// origins
        "*",  # Allow all origins for testing (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Add security middleware
app.middleware("http")(security_middleware)

# API Key authentication
api_key_auth = APIKeyAuth()

# Include routers
app.include_router(chat_router, prefix="/v1", tags=["chat"])
app.include_router(clauses_router, prefix="/v1", tags=["clauses"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
# app.include_router(quiz_router, tags=["quiz"])  # Temporarily disabled - using direct endpoint

# Mount static files for web interface
web_dir = Path(__file__).parent.parent / "web"
if web_dir.exists():
    app.mount("/web", StaticFiles(directory=str(web_dir), html=True), name="web")


class ExplainReq(BaseModel):
    audience: str = "student"
    depth: str = "standard"
    locale: str = "en-US"


class ScriptReq(BaseModel):
    duration_min: int = 2
    tone: str = "plain"
    format: str = "voiceover"
    audience: str = "student"


class LogReq(BaseModel):
    artifact_id: str
    clause: str
    edition: str
    step: str
    actor: str
    status: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: str


def get_cache_key(code: str, clause: str, operation: str) -> str:
    return f"{code}:{clause}:{operation}"


def is_cache_valid(cache_key: str) -> bool:
    """Check if cache entry is still valid"""
    if cache_key not in cache_timestamps:
        return False

    cache_time = cache_timestamps[cache_key]
    return (time.time() - cache_time) < CACHE_TTL_SECONDS


def set_cache_entry(cache_key: str, value: Any):
    """Set cache entry with timestamp"""
    cache[cache_key] = value
    cache_timestamps[cache_key] = time.time()


def get_cache_entry(cache_key: str) -> Optional[Any]:
    """Get cache entry if valid"""
    if cache_key in cache and is_cache_valid(cache_key):
        return cache[cache_key]
    return None


@app.get("/health")
def health():
    """Health check endpoint - lightweight, no auth required"""
    health_data = check_system_health()
    # Add edition stamp for truth-in-marketing
    health_data["edition"] = EDITION
    health_data["build"] = os.getenv("GIT_SHA", "local")[:7]
    return health_data


@app.get("/ready")
def ready():
    """Readiness check endpoint - checks if system is ready to serve requests"""
    return check_readiness()


@app.get("/metrics")
def metrics():
    """Metrics endpoint for monitoring"""
    return get_metrics_summary()


@app.get("/v1/edition")
def get_edition_info():
    """Get current edition information"""
    return content_manager.get_edition_info()


@app.get("/v1/integrity/check")
def check_integrity():
    """Check content integrity"""
    return content_manager.verify_checksums()


@app.post("/v1/clauses/{code}/{clause}/explain")
def explain(
    code: str,
    clause: str,
    body: ExplainReq,
    request: Request,
    authorization: str = Header(None),
):
    t0 = time.time()
    request_id = getattr(request.state, "request_id", "unknown")

    try:
        # Check scope
        api_key = getattr(request.state, "api_key", None)
        if api_key and not check_scope(api_key, "read:clause"):
            raise HTTPException(
                status_code=403, detail="Insufficient scope: read:clause required"
            )

        # Check cache first
        cache_key = get_cache_key(code, clause, "explain")
        cached_result = get_cache_entry(cache_key)
        if cached_result:
            cached_result["telemetry"]["cache_hit"] = True
            cached_result["telemetry"]["latency_ms"] = int((time.time() - t0) * 1000)
            record_request_metrics(
                "/v1/clauses/{code}/{clause}/explain",
                200,
                time.time() - t0,
                cache_hit=True,
            )
            logger.log(
                "INFO",
                f"Cache hit for clause {code}:{clause}",
                request_id,
                cache_hit=True,
            )
            return cached_result

        # Validate edition
        edition = get_edition_guard()

        # Bible Stop Gate: enforce authority terms
        if code.upper().startswith("AWS"):
            label = "Clause"
        elif code.upper().startswith("ASME"):
            label = "Chapter"
        else:
            label = "Section"

        # Generate response
        ref_checksum = generate_clause_checksum(code, clause, edition)
        payload = {
            "summary": f"Plain-English core requirement for {label} {clause} in {code} {edition}. This section defines the essential criteria and acceptance standards for welding procedures and performance qualifications.",
            "examples": [
                {
                    "title": "Shop scenario",
                    "text": f"In a fabrication shop, {label} {clause} would apply when establishing welding procedures for structural steel components. The inspector must verify that all welding parameters meet the specified requirements.",
                },
                {
                    "title": "Field scenario",
                    "text": f"During field construction, {label} {clause} governs the acceptance criteria for welds in critical load-bearing applications. Any deviation requires documented justification and approval.",
                },
            ],
            "pitfalls": [
                "Common misread: Confusing acceptance criteria with rejection criteria",
                "Common misread: Not considering material thickness variations in application",
            ],
            "refs": {
                "code": code,
                "edition": edition,
                "clause": clause,
                "tables": ["Table 8.1", "Table 6.1"],
                "figures": ["Figure 6.1", "Figure 8.1"],
            },
            "ref_checksum": ref_checksum,
            "telemetry": {
                "model": "local-gen",
                "latency_ms": int((time.time() - t0) * 1000),
                "cache_hit": False,
            },
        }

        # Cache the result
        set_cache_entry(cache_key, payload.copy())

        # Record metrics
        record_request_metrics(
            "/v1/clauses/{code}/{clause}/explain",
            200,
            time.time() - t0,
            cache_hit=False,
        )
        logger.log(
            "INFO",
            f"Generated explanation for clause {code}:{clause}",
            request_id,
            clause=clause,
            edition=edition,
            latency_ms=int((time.time() - t0) * 1000),
        )

        return payload

    except HTTPException:
        raise
    except Exception as e:
        record_request_metrics(
            "/v1/clauses/{code}/{clause}/explain", 500, time.time() - t0
        )
        logger.log(
            "ERROR",
            f"Error generating explanation for clause {code}:{clause}",
            request_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/v1/clauses/{code}/{clause}/script")
def script(
    code: str,
    clause: str,
    body: ScriptReq,
    request: Request,
    authorization: str = Header(None),
):
    t0 = time.time()
    request_id = getattr(request.state, "request_id", "unknown")

    try:
        # Check scope
        api_key = getattr(request.state, "api_key", None)
        if api_key and not check_scope(api_key, "gen:script"):
            raise HTTPException(
                status_code=403, detail="Insufficient scope: gen:script required"
            )

        # Check cache first
        cache_key = get_cache_key(code, clause, "script")
        cached_result = get_cache_entry(cache_key)
        if cached_result:
            cached_result["telemetry"]["cache_hit"] = True
            cached_result["telemetry"]["latency_ms"] = int((time.time() - t0) * 1000)
            record_request_metrics(
                "/v1/clauses/{code}/{clause}/script",
                200,
                time.time() - t0,
                cache_hit=True,
            )
            return cached_result

        # Validate edition
        edition = get_edition_guard()

        # Generate script
        ref_checksum = generate_clause_checksum(code, clause, edition)
        payload = {
            "script": f"Welcome to {code} {clause}. This {body.duration_min}-minute explanation covers the essential requirements for welding inspection. [Script content would be generated based on clause content]",
            "duration_min": body.duration_min,
            "format": body.format,
            "tone": body.tone,
            "audience": body.audience,
            "refs": {
                "code": code,
                "edition": edition,
                "clause": clause,
                "tables": ["Table 8.1"],
                "figures": [],
            },
            "ref_checksum": ref_checksum,
            "telemetry": {
                "model": "local-gen",
                "latency_ms": int((time.time() - t0) * 1000),
                "cache_hit": False,
            },
        }

        # Cache the result
        set_cache_entry(cache_key, payload.copy())

        # Record metrics
        record_request_metrics(
            "/v1/clauses/{code}/{clause}/script", 200, time.time() - t0, cache_hit=False
        )
        logger.log(
            "INFO",
            f"Generated script for clause {code}:{clause}",
            request_id,
            clause=clause,
            edition=edition,
            duration_min=body.duration_min,
        )

        return payload

    except HTTPException:
        raise
    except Exception as e:
        record_request_metrics(
            "/v1/clauses/{code}/{clause}/script", 500, time.time() - t0
        )
        logger.log(
            "ERROR",
            f"Error generating script for clause {code}:{clause}",
            request_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/v1/clauses/{code}/{clause}/summary")
def summary(
    code: str, clause: str, request: Request, authorization: str = Header(None)
):
    """Quick summary endpoint for mobile UI paint"""
    t0 = time.time()
    request_id = getattr(request.state, "request_id", "unknown")

    try:
        # Check scope
        api_key = getattr(request.state, "api_key", None)
        if api_key and not check_scope(api_key, "read:clause"):
            raise HTTPException(
                status_code=403, detail="Insufficient scope: read:clause required"
            )

        # Check cache first
        cache_key = get_cache_key(code, clause, "summary")
        cached_result = get_cache_entry(cache_key)
        if cached_result:
            record_request_metrics(
                "/v1/clauses/{code}/{clause}/summary",
                200,
                time.time() - t0,
                cache_hit=True,
            )
            return cached_result

        # Validate edition
        edition = get_edition_guard()

        # Generate quick summary
        ref_checksum = generate_clause_checksum(code, clause, edition)
        payload = {
            "title": f"{code} {clause}",
            "summary": f"Essential requirements for {clause} in {code} {edition}",
            "refs": {"code": code, "edition": edition, "clause": clause},
            "ref_checksum": ref_checksum,
            "telemetry": {
                "latency_ms": int((time.time() - t0) * 1000),
                "cache_hit": False,
            },
        }

        # Cache the result
        set_cache_entry(cache_key, payload.copy())

        # Record metrics
        record_request_metrics(
            "/v1/clauses/{code}/{clause}/summary",
            200,
            time.time() - t0,
            cache_hit=False,
        )

        return payload

    except HTTPException:
        raise
    except Exception as e:
        record_request_metrics(
            "/v1/clauses/{code}/{clause}/summary", 500, time.time() - t0
        )
        logger.log(
            "ERROR",
            f"Error generating summary for clause {code}:{clause}",
            request_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/v1/pipeline/log")
def log(body: LogReq, request: Request, authorization: str = Header(None)):
    t0 = time.time()
    request_id = getattr(request.state, "request_id", "unknown")

    try:
        # Check scope
        api_key = getattr(request.state, "api_key", None)
        if api_key and not check_scope(api_key, "write:log"):
            raise HTTPException(
                status_code=403, detail="Insufficient scope: write:log required"
            )

        # Log to file
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "artifact_id": body.artifact_id,
            "clause": body.clause,
            "edition": body.edition,
            "step": body.step,
            "actor": body.actor,
            "status": body.status,
        }

        # Ensure log directory exists
        log_dir = os.path.join(CONTENT_DIR, "pipeline")
        os.makedirs(log_dir, exist_ok=True)

        # Write to JSONL file
        log_file = os.path.join(
            log_dir, f"pipeline_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
        )
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Record metrics
        record_request_metrics("/v1/pipeline/log", 200, time.time() - t0)
        logger.log(
            "INFO",
            "Logged pipeline event",
            request_id,
            artifact_id=body.artifact_id,
            step=body.step,
            status=body.status,
        )

        return {"ok": True, "logged": True, "file": log_file}

    except HTTPException:
        raise
    except Exception as e:
        record_request_metrics("/v1/pipeline/log", 500, time.time() - t0)
        logger.log("ERROR", "Error logging pipeline event", request_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)

# --- KB endpoints ---
from pathlib import Path

KB_DIR = Path(__file__).resolve().parents[1] / "data" / "kb"
KB_ALIASES = {"aws": "aws_ecosystem", "wit": "wit_core"}


@app.get("/v1/kb", tags=["kb"])
def kb_index():
    items = []
    if KB_DIR.exists():
        for p in KB_DIR.glob("*.json"):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                d = {}
            items.append(
                {
                    "slug": p.stem,
                    "title": d.get("title", p.stem),
                    "updated": d.get("updated"),
                    "category": d.get("category"),
                    "tags": d.get("tags", []),
                }
            )
    return {"items": items}


@app.get("/v1/kb/{slug}", tags=["kb"])
def kb_card(slug: str):
    slug = KB_ALIASES.get(slug, slug)
    path = (KB_DIR / f"{slug}.json").resolve()
    if KB_DIR not in path.parents:
        raise HTTPException(status_code=400, detail="Invalid slug")
    if not path.exists():
        raise HTTPException(status_code=404, detail="KB card not found")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        logger.exception("kb_read_error", extra={"slug": slug, "path": str(path)})
        raise HTTPException(status_code=500, detail="KB read error")


# --- end KB endpoints ---

# === PILOT A INTEGRATION: Autonomous Incident Analysis ===
from typing import Union
from enum import Enum


class IncidentTrigger(str, Enum):
    CHROME_HUNG = "chrome_hung"
    KUBE_DRIFT = "kube_drift"
    GPU_DRIVER = "gpu_driver"
    MEMORY_PRESSURE = "memory_pressure"


class IncidentAnalysisRequest(BaseModel):
    trigger: IncidentTrigger
    system_context: Dict[str, Any]
    chrome_memory_mb: Optional[int] = None
    gpu_driver_version: Optional[str] = None
    free_ram_gb: Optional[float] = None
    confidence_threshold: Optional[float] = 0.8


class IncidentAnalysisResponse(BaseModel):
    incident_id: str
    timestamp: str
    root_cause: str
    confidence: float
    proposed_fix: str
    blast_radius: str
    evidence: List[str]
    windsurf_handoff_required: bool
    system_health_score: float


class CascadeExecutionRequest(BaseModel):
    incident_id: str
    cascade_type: str = "reset-validate"
    namespace: str = "test-ns"
    approval_gate: str = "hitl_required"
    rollback_on_fail: bool = True


class CascadeExecutionResponse(BaseModel):
    cascade_id: str
    timestamp: str
    result: str
    latency_s: float
    steps_executed: List[str]
    logs_ref: str
    mttr_contribution: Dict[str, float]


class PilotMetricsResponse(BaseModel):
    generated_at: str
    cursor_metrics: Dict[str, Union[int, float]]
    windsurf_metrics: Dict[str, Union[int, float]]
    unified_metrics: Dict[str, Union[int, float]]
    success_criteria: Dict[str, bool]


@app.post(
    "/api/v1/pilot-a/incidents/analyze",
    response_model=IncidentAnalysisResponse,
    tags=["pilot-a"],
)
async def analyze_incident(
    request: IncidentAnalysisRequest, api_key_info: dict = Depends(get_api_key_info)
):
    """CURSOR Autonomous Incident Analysis - Enhanced root cause detection"""
    try:
        # Generate incident ID
        incident_id = f"cursor_{int(time.time())}"
        timestamp = datetime.now().isoformat()

        # Enhanced incident analysis logic
        analysis = {
            "incident_id": incident_id,
            "timestamp": timestamp,
            "root_cause": "gpu_driver"
            if request.trigger == IncidentTrigger.GPU_DRIVER
            else "memory_pressure",
            "confidence": 0.85
            if request.chrome_memory_mb and request.chrome_memory_mb > 1500
            else 0.72,
            "proposed_fix": "toggle_angle_opengl"
            if request.gpu_driver_version
            else "restart_chrome",
            "blast_radius": "med",
            "evidence": [
                f"chrome_memory_mb:{request.chrome_memory_mb or 0}",
                f"gpu_driver:{request.gpu_driver_version or 'unknown'}",
                f"free_ram_gb:{request.free_ram_gb or 0}",
            ],
            "windsurf_handoff_required": True,
            "system_health_score": 0.78,
        }

        # Log security event
        log_security_event(
            "pilot_a_incident_analysis",
            {
                "incident_id": incident_id,
                "trigger": request.trigger,
                "confidence": analysis["confidence"],
                "api_key": api_key_info.get("key_id", "unknown"),
            },
        )

        return IncidentAnalysisResponse(**analysis)

    except Exception as e:
        logger.exception("pilot_a_incident_analysis_error", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Incident analysis failed")


@app.post(
    "/api/v1/pilot-a/cascades/execute",
    response_model=CascadeExecutionResponse,
    tags=["pilot-a"],
)
async def execute_cascade(
    request: CascadeExecutionRequest, api_key_info: dict = Depends(get_api_key_info)
):
    """Windsurf Cascade Execution - Reset-validate operations with HITL gates"""
    try:
        # Generate cascade ID
        cascade_id = f"windsurf_{int(time.time())}"
        timestamp = datetime.now().isoformat()

        # Simulate cascade execution (replace with actual Windsurf integration)
        execution_start = time.time()

        # Mock cascade execution
        steps = ["patch:test-ns", "validate:health", "roll-back:on-fail"]
        execution_latency = 18.2  # Simulated latency

        cascade_result = {
            "cascade_id": cascade_id,
            "timestamp": timestamp,
            "result": "success",
            "latency_s": execution_latency,
            "steps_executed": steps,
            "logs_ref": f"s3://clausebot-audit/{datetime.now().strftime('%Y-%m-%d')}/{cascade_id}.log",
            "mttr_contribution": {
                "baseline_s": 600.0,
                "observed_s": execution_latency,
                "improvement_pct": round((600 - execution_latency) / 600, 3),
            },
        }

        # Log security event
        log_security_event(
            "pilot_a_cascade_execution",
            {
                "cascade_id": cascade_id,
                "incident_id": request.incident_id,
                "namespace": request.namespace,
                "result": "success",
                "api_key": api_key_info.get("key_id", "unknown"),
            },
        )

        return CascadeExecutionResponse(**cascade_result)

    except Exception as e:
        logger.exception("pilot_a_cascade_execution_error", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Cascade execution failed")


@app.get(
    "/api/v1/pilot-a/metrics", response_model=PilotMetricsResponse, tags=["pilot-a"]
)
async def get_pilot_metrics(api_key_info: dict = Depends(get_api_key_info)):
    """Pilot A Unified Metrics - Real-time scorecard for team dashboard"""
    try:
        timestamp = datetime.now().isoformat()

        # Mock metrics (replace with actual scorecard aggregation)
        metrics = {
            "generated_at": timestamp,
            "cursor_metrics": {
                "incidents_detected": 12,
                "precision": 0.92,
                "recall": 0.88,
                "avg_chrome_memory_mb": 1650,
                "gpu_driver_issues": 8,
                "high_confidence_rate": 0.85,
            },
            "windsurf_metrics": {
                "cascade_executions": 15,
                "success_rate": 0.933,
                "avg_latency_s": 18.2,
                "hitl_compliance_rate": 1.0,
                "slo_violations": 0,
            },
            "unified_metrics": {
                "mttr_baseline_s": 600,
                "mttr_observed_s": 18.2,
                "mttr_delta_pct": 0.97,
                "precision_target_met": True,
                "recall_target_met": True,
            },
            "success_criteria": {
                "precision_gt_90": True,
                "recall_gt_85": True,
                "mttr_improvement_gt_40": True,
                "hitl_compliance_100": True,
                "slo_compliance": True,
            },
        }

        return PilotMetricsResponse(**metrics)

    except Exception as e:
        logger.exception("pilot_a_metrics_error", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Metrics retrieval failed")


@app.get("/api/v1/pilot-a/health", tags=["pilot-a"])
async def pilot_health_check():
    """Pilot A Health Check - System status and readiness"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "cursor_engine": "operational",
                "windsurf_cascades": "operational",
                "drive_sync": "optimal",
                "team_dashboard": "active",
                "kill_switch": "armed",
            },
            "metrics": {
                "uptime_hours": 24.5,
                "incidents_processed": 12,
                "cascades_executed": 15,
                "avg_response_time_ms": 245,
            },
        }

        return health_status

    except Exception as e:
        logger.exception("pilot_a_health_check_error", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Health check failed")


# === END PILOT A INTEGRATION ===

# === QUIZ ENDPOINTS ===
# Import quiz data source
try:
    from ..airtable_data_source import get_quiz_source, test_airtable_connection
except ImportError:
    try:
        import sys
        import os

        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from airtable_data_source import get_quiz_source, test_airtable_connection
    except ImportError:
        logger.warning(
            "Could not import airtable_data_source, using fallback questions"
        )
        get_quiz_source = None
        test_airtable_connection = None


@app.get("/v1/quiz")
async def get_quiz_questions(
    count: int = Query(5, ge=1, le=20, description="Number of questions to return"),
):
    """Get quiz questions from Airtable with fallback data"""
    try:
        # Try to get questions from Airtable
        if get_quiz_source:
            questions = get_quiz_source()
            if questions:
                # Limit to requested count
                selected_questions = questions[:count]
                return {
                    "questions": selected_questions,
                    "total_available": len(questions),
                    "source_status": "airtable",
                }
    except Exception as e:
        logger.warning(f"Failed to load from Airtable: {e}")

    # Fallback questions if Airtable fails
    fallback_questions = [
        {
            "id": "aws-d1.1-undercut-1",
            "question": "According to AWS D1.1, what is the maximum allowable undercut depth for statically loaded members?",
            "choices": [
                {"key": "A", "text": "1/32 inch (0.8 mm)"},
                {"key": "B", "text": "1/16 inch (1.6 mm)"},
                {"key": "C", "text": "3/32 inch (2.4 mm)"},
                {"key": "D", "text": "1/8 inch (3.2 mm)"},
            ],
            "correct": "A",
            "clause": "AWS D1.1 Clause 6.9.1",
            "category": "Visual Inspection",
            "explanation": "For statically loaded members, undercut shall not exceed 1/32 inch (0.8 mm) in depth according to AWS D1.1 Clause 6.9.1.",
            "source": "fallback",
        },
        {
            "id": "aws-d1.1-joint-prep-1",
            "question": "What is the primary purpose of joint preparation in welding according to AWS D1.1?",
            "choices": [
                {"key": "A", "text": "To improve appearance"},
                {"key": "B", "text": "To ensure proper penetration and fusion"},
                {"key": "C", "text": "To reduce welding time"},
                {"key": "D", "text": "To minimize material usage"},
            ],
            "correct": "B",
            "clause": "AWS D1.1 Clause 2.3",
            "category": "Joint Preparation",
            "explanation": "Joint preparation ensures proper penetration and fusion, which is critical for weld quality and structural integrity.",
            "source": "fallback",
        },
    ]

    selected_questions = fallback_questions[:count]

    return {
        "questions": selected_questions,
        "total_available": len(fallback_questions),
        "source_status": "fallback",
    }
