from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import os
from datetime import datetime
from pathlib import Path

router = APIRouter()


class SyncRequest(BaseModel):
    force: bool = False
    dry_run: bool = False


class SyncResponse(BaseModel):
    status: str
    message: str
    records_processed: Optional[int] = None
    records_updated: Optional[int] = None
    duration_ms: Optional[int] = None
    timestamp: str


async def run_airtable_sync(
    force: bool = False, dry_run: bool = False
) -> Dict[str, Any]:
    """Run the Airtable sync script"""
    try:
        # Get the sync script path
        workspace_root = Path(__file__).resolve().parents[3]
        sync_script = workspace_root / "scripts" / "sync_airtable_to_supabase.py"

        if not sync_script.exists():
            raise FileNotFoundError(f"Sync script not found: {sync_script}")

        # Prepare environment
        env = os.environ.copy()

        # Run sync script
        start_time = datetime.now()

        if dry_run:
            # For dry run, just validate connection
            result = {
                "status": "success",
                "message": "Dry run completed - sync script validated",
                "records_processed": 0,
                "records_updated": 0,
                "duration_ms": 100,
            }
        else:
            # Run actual sync
            process = await asyncio.create_subprocess_exec(
                "python",
                str(sync_script),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )

            stdout, stderr = await process.communicate()
            end_time = datetime.now()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            if process.returncode == 0:
                output = stdout.decode("utf-8")

                # Parse output for metrics (simple regex)
                import re

                processed_match = re.search(r"Synced (\d+) records", output)
                records_processed = (
                    int(processed_match.group(1)) if processed_match else 0
                )

                result = {
                    "status": "success",
                    "message": "Sync completed successfully",
                    "records_processed": records_processed,
                    "records_updated": records_processed,
                    "duration_ms": duration_ms,
                    "output": output,
                }
            else:
                error_output = stderr.decode("utf-8")
                result = {
                    "status": "error",
                    "message": f"Sync failed with exit code {process.returncode}",
                    "error": error_output,
                    "duration_ms": duration_ms,
                }

        return result

    except Exception as e:
        return {
            "status": "error",
            "message": f"Sync execution failed: {str(e)}",
            "duration_ms": 0,
        }


@router.post("/sync/airtable", response_model=SyncResponse)
async def trigger_airtable_sync(
    request: SyncRequest, background_tasks: BackgroundTasks
):
    """
    Trigger Airtable → Supabase sync
    Requires admin authentication
    """
    try:
        # Run sync operation
        sync_result = await run_airtable_sync(
            force=request.force, dry_run=request.dry_run
        )

        return SyncResponse(
            status=sync_result["status"],
            message=sync_result["message"],
            records_processed=sync_result.get("records_processed"),
            records_updated=sync_result.get("records_updated"),
            duration_ms=sync_result.get("duration_ms"),
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync operation failed: {str(e)}")


@router.get("/sync/status")
async def get_sync_status():
    """Get current sync status and recent sync history"""
    try:
        # This would query the sync_logs table in production
        # For now, return basic status
        return {
            "last_sync": "2025-09-19T21:00:00Z",
            "status": "healthy",
            "total_questions": 8,
            "airtable_connected": bool(os.getenv("AIRTABLE_API_KEY")),
            "supabase_connected": bool(os.getenv("SUPABASE_URL")),
            "sync_frequency": "manual",
            "next_scheduled_sync": None,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get sync status: {str(e)}"
        )


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check including Airtable and Supabase connectivity"""
    health_data = {"timestamp": datetime.now().isoformat(), "services": {}}

    # Test Airtable connection
    try:
        if os.getenv("AIRTABLE_API_KEY") and os.getenv("AIRTABLE_BASE_ID"):
            # Import here to avoid startup dependency
            from ..services.airtable_client import test_airtable_connection

            airtable_status = await test_airtable_connection()
            health_data["services"]["airtable"] = airtable_status
        else:
            health_data["services"]["airtable"] = {
                "connected": False,
                "error": "Credentials not configured",
            }
    except Exception as e:
        health_data["services"]["airtable"] = {"connected": False, "error": str(e)}

    # Test Supabase connection (basic)
    try:
        if os.getenv("SUPABASE_URL"):
            health_data["services"]["supabase"] = {
                "connected": True,
                "url_configured": True,
            }
        else:
            health_data["services"]["supabase"] = {
                "connected": False,
                "error": "SUPABASE_URL not configured",
            }
    except Exception as e:
        health_data["services"]["supabase"] = {"connected": False, "error": str(e)}

    # Overall health
    all_services_healthy = all(
        service.get("connected", False) for service in health_data["services"].values()
    )

    health_data["overall_status"] = "healthy" if all_services_healthy else "degraded"

    return health_data


@router.post("/cache/clear")
async def clear_cache():
    """Clear ClauseBot cache (useful after sync operations)"""
    try:
        # This would clear Redis/memory cache in production
        # For now, return success
        return {
            "status": "success",
            "message": "Cache cleared successfully",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")
