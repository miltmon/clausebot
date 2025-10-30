"""
🔧 ClauseBot Sync Admin API Routes
Admin endpoints for managing Airtable → Supabase sync operations
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from pydantic import BaseModel

from ..services.airtable_sync import (
    AirtableSyncService,
    sync_all_tables,
    sync_single_table,
    get_sync_status,
)
from ..middleware.auth import require_admin_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/sync", tags=["sync-admin"])


class SyncRequest(BaseModel):
    """Request model for sync operations"""

    tables: Optional[List[str]] = None
    force: bool = False
    dry_run: bool = False


class SyncResponse(BaseModel):
    """Response model for sync operations"""

    job_id: Optional[str] = None
    status: str
    message: str
    results: Optional[Dict[str, Any]] = None


@router.get("/status")
async def get_sync_status_endpoint(
    admin_key: str = Depends(require_admin_key),
) -> Dict[str, Any]:
    """Get current sync status for all tables"""
    try:
        status_data = await get_sync_status()

        # Get recent sync jobs
        from ..services.airtable_sync import create_client
        import os

        supabase = create_client(
            os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )

        recent_jobs = (
            supabase.table("airtable_sync_jobs")
            .select("*")
            .order("started_at", desc=True)
            .limit(10)
            .execute()
        )

        return {
            "table_status": status_data,
            "recent_jobs": recent_jobs.data,
            "overall_health": _assess_sync_health(status_data),
        }

    except Exception as e:
        logger.error(f"Failed to get sync status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger")
async def trigger_sync(
    request: SyncRequest,
    background_tasks: BackgroundTasks,
    admin_key: str = Depends(require_admin_key),
) -> SyncResponse:
    """Trigger sync operation for specified tables or all tables"""
    try:
        if request.dry_run:
            # Dry run - validate configuration without syncing
            return await _dry_run_sync(request.tables)

        # Trigger actual sync in background
        if request.tables:
            # Sync specific tables
            background_tasks.add_task(
                _sync_specific_tables, request.tables, request.force
            )
            message = f"Sync triggered for tables: {', '.join(request.tables)}"
        else:
            # Sync all tables
            background_tasks.add_task(_sync_all_tables_background, request.force)
            message = "Full sync triggered for all tables"

        return SyncResponse(status="triggered", message=message)

    except Exception as e:
        logger.error(f"Failed to trigger sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/{table_name}")
async def sync_table_endpoint(
    table_name: str,
    background_tasks: BackgroundTasks,
    force: bool = Query(False, description="Force sync even if no changes detected"),
    admin_key: str = Depends(require_admin_key),
) -> SyncResponse:
    """Sync a specific table"""
    try:
        # Validate table name
        async with AirtableSyncService() as sync_service:
            if table_name not in sync_service.mapping["tables"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown table: {table_name}. Available: {list(sync_service.mapping['tables'].keys())}",
                )

        # Trigger sync in background
        background_tasks.add_task(_sync_single_table_background, table_name, force)

        return SyncResponse(
            status="triggered", message=f"Sync triggered for table: {table_name}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to sync table {table_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs")
async def get_sync_jobs(
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by job status"),
    admin_key: str = Depends(require_admin_key),
) -> Dict[str, Any]:
    """Get sync job history"""
    try:
        from ..services.airtable_sync import create_client
        import os

        supabase = create_client(
            os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )

        query = supabase.table("airtable_sync_jobs").select("*")

        if status:
            query = query.eq("status", status)

        jobs = query.order("started_at", desc=True).limit(limit).execute()

        return {"jobs": jobs.data, "total_count": len(jobs.data)}

    except Exception as e:
        logger.error(f"Failed to get sync jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_sync_config(
    admin_key: str = Depends(require_admin_key),
) -> Dict[str, Any]:
    """Get current sync configuration"""
    try:
        async with AirtableSyncService() as sync_service:
            # Return sanitized config (no API keys)
            config = sync_service.mapping.copy()
            config.pop("api_key_env", None)

            return {
                "config": config,
                "tables_configured": list(config["tables"].keys()),
                "sync_interval_minutes": config.get("sync_schedule", {}).get(
                    "interval_minutes", 10
                ),
            }

    except Exception as e:
        logger.error(f"Failed to get sync config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_sync_config(
    admin_key: str = Depends(require_admin_key),
) -> Dict[str, Any]:
    """Validate sync configuration and connectivity"""
    try:
        validation_results = {}

        # Test Airtable connectivity
        try:
            async with AirtableSyncService() as sync_service:
                # Test fetching one record from each table
                for table_name, table_config in sync_service.mapping["tables"].items():
                    try:
                        # Fetch just one record to test connectivity
                        test_records = await sync_service._fetch_airtable_data(
                            {**table_config, "test_mode": True}
                        )

                        validation_results[table_name] = {
                            "status": "success",
                            "record_count": len(test_records),
                            "message": f"Successfully connected to {table_config['table']}",
                        }

                    except Exception as e:
                        validation_results[table_name] = {
                            "status": "error",
                            "message": str(e),
                        }

        except Exception as e:
            return {
                "overall_status": "error",
                "message": f"Failed to initialize sync service: {e}",
                "table_results": {},
            }

        # Determine overall status
        error_count = sum(
            1 for r in validation_results.values() if r["status"] == "error"
        )
        overall_status = "error" if error_count > 0 else "success"

        return {
            "overall_status": overall_status,
            "table_results": validation_results,
            "errors": error_count,
            "total_tables": len(validation_results),
        }

    except Exception as e:
        logger.error(f"Failed to validate sync config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def sync_health_check() -> Dict[str, Any]:
    """Health check for sync system (no auth required)"""
    try:
        status_data = await get_sync_status()
        health = _assess_sync_health(status_data)

        return {
            "status": health["overall_status"],
            "last_successful_sync": health.get("last_successful_sync"),
            "tables_healthy": health.get("tables_healthy", 0),
            "tables_total": len(status_data),
        }

    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# Background task functions
async def _sync_all_tables_background(force: bool = False):
    """Background task to sync all tables"""
    try:
        logger.info("Starting background sync for all tables")
        results = await sync_all_tables()

        # Log results
        for table_name, result in results.items():
            if result.errors:
                logger.error(f"Sync errors for {table_name}: {result.errors}")
            else:
                logger.info(
                    f"Sync completed for {table_name}: "
                    f"{result.records_created} created, {result.records_updated} updated"
                )

    except Exception as e:
        logger.error(f"Background sync failed: {e}")


async def _sync_specific_tables(table_names: List[str], force: bool = False):
    """Background task to sync specific tables"""
    try:
        logger.info(f"Starting background sync for tables: {table_names}")

        for table_name in table_names:
            try:
                result = await sync_single_table(table_name)
                if result.errors:
                    logger.error(f"Sync errors for {table_name}: {result.errors}")
                else:
                    logger.info(
                        f"Sync completed for {table_name}: "
                        f"{result.records_created} created, {result.records_updated} updated"
                    )
            except Exception as e:
                logger.error(f"Failed to sync table {table_name}: {e}")

    except Exception as e:
        logger.error(f"Background sync failed: {e}")


async def _sync_single_table_background(table_name: str, force: bool = False):
    """Background task to sync a single table"""
    try:
        logger.info(f"Starting background sync for table: {table_name}")
        result = await sync_single_table(table_name)

        if result.errors:
            logger.error(f"Sync errors for {table_name}: {result.errors}")
        else:
            logger.info(
                f"Sync completed for {table_name}: "
                f"{result.records_created} created, {result.records_updated} updated"
            )

    except Exception as e:
        logger.error(f"Background sync failed for {table_name}: {e}")


async def _dry_run_sync(table_names: Optional[List[str]] = None) -> SyncResponse:
    """Perform dry run validation"""
    try:
        async with AirtableSyncService() as sync_service:
            results = {}

            tables_to_check = table_names or list(sync_service.mapping["tables"].keys())

            for table_name in tables_to_check:
                table_config = sync_service.mapping["tables"][table_name]

                try:
                    # Fetch and validate records without syncing
                    airtable_records = await sync_service._fetch_airtable_data(
                        table_config
                    )

                    valid_records = 0
                    invalid_records = 0

                    for record in airtable_records[:10]:  # Sample first 10 records
                        try:
                            transformed = await sync_service._transform_record(
                                record, table_config
                            )
                            if transformed:
                                valid_records += 1
                            else:
                                invalid_records += 1
                        except Exception:
                            invalid_records += 1

                    results[table_name] = {
                        "total_records": len(airtable_records),
                        "sample_valid": valid_records,
                        "sample_invalid": invalid_records,
                        "status": "ready",
                    }

                except Exception as e:
                    results[table_name] = {"status": "error", "error": str(e)}

            return SyncResponse(
                status="dry_run_complete",
                message="Dry run validation completed",
                results=results,
            )

    except Exception as e:
        return SyncResponse(status="error", message=f"Dry run failed: {e}")


def _assess_sync_health(status_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Assess overall sync health"""
    if not status_data:
        return {"overall_status": "unknown", "message": "No sync status data available"}

    healthy_tables = 0
    stale_tables = 0
    error_tables = 0
    never_synced = 0
    last_successful_sync = None

    for table_status in status_data:
        status = table_status.get("status", "unknown")

        if status == "healthy":
            healthy_tables += 1
        elif status == "stale":
            stale_tables += 1
        elif status == "errors":
            error_tables += 1
        elif status == "never_synced":
            never_synced += 1

        # Track most recent successful sync
        table_last_sync = table_status.get("last_successful_sync_at")
        if table_last_sync and (
            not last_successful_sync or table_last_sync > last_successful_sync
        ):
            last_successful_sync = table_last_sync

    total_tables = len(status_data)

    # Determine overall status
    if error_tables > 0 or never_synced > 0:
        overall_status = "unhealthy"
    elif stale_tables > total_tables // 2:
        overall_status = "degraded"
    else:
        overall_status = "healthy"

    return {
        "overall_status": overall_status,
        "tables_healthy": healthy_tables,
        "tables_stale": stale_tables,
        "tables_errors": error_tables,
        "tables_never_synced": never_synced,
        "total_tables": total_tables,
        "last_successful_sync": last_successful_sync,
    }
