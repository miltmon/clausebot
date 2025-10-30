"""
🍽️ ClauseBot Airtable Sync Service
Syncs authoring data from Airtable to Supabase runtime tables
"""

import asyncio
import json
import hashlib
import re
import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import httpx
from supabase import create_client, Client

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Result of a sync operation"""

    table_name: str
    records_processed: int = 0
    records_created: int = 0
    records_updated: int = 0
    records_deleted: int = 0
    errors: List[str] = None
    duration_seconds: float = 0.0

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class AirtableSyncService:
    """Service to sync data from Airtable to Supabase"""

    def __init__(self, mapping_file: str = "ops/airtable_sync_mapping.json"):
        self.mapping_file = mapping_file
        self.mapping = self._load_mapping()
        self.airtable_api_key = os.getenv(
            self.mapping.get("api_key_env", "AIRTABLE_API_KEY")
        )
        self.supabase = self._init_supabase()
        self.http_client = None

        if not self.airtable_api_key:
            raise ValueError("Airtable API key not found in environment")

    def _load_mapping(self) -> Dict[str, Any]:
        """Load sync mapping configuration"""
        try:
            with open(self.mapping_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Mapping file not found: {self.mapping_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in mapping file: {e}")

    def _init_supabase(self) -> Client:
        """Initialize Supabase client"""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not url or not key:
            raise ValueError("Supabase URL and service role key required")

        return create_client(url, key)

    async def __aenter__(self):
        """Async context manager entry"""
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.mapping["sync_config"]["timeout_seconds"]),
            limits=httpx.Limits(
                max_connections=self.mapping["performance"]["max_concurrent_requests"]
            ),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.http_client:
            await self.http_client.aclose()

    async def sync_all_tables(self) -> Dict[str, SyncResult]:
        """Sync all configured tables"""
        results = {}

        # Start sync job tracking
        job_id = await self._start_sync_job("full")

        try:
            # Sync tables in parallel if configured
            if self.mapping["performance"]["parallel_tables"]:
                tasks = [
                    self.sync_table(table_name)
                    for table_name in self.mapping["tables"].keys()
                ]
                sync_results = await asyncio.gather(*tasks, return_exceptions=True)

                for table_name, result in zip(
                    self.mapping["tables"].keys(), sync_results
                ):
                    if isinstance(result, Exception):
                        results[table_name] = SyncResult(
                            table_name=table_name, errors=[str(result)]
                        )
                    else:
                        results[table_name] = result
            else:
                # Sequential sync
                for table_name in self.mapping["tables"].keys():
                    try:
                        results[table_name] = await self.sync_table(table_name)
                    except Exception as e:
                        results[table_name] = SyncResult(
                            table_name=table_name, errors=[str(e)]
                        )

            # Update job completion
            await self._complete_sync_job(job_id, results)

        except Exception as e:
            await self._fail_sync_job(job_id, str(e))
            raise

        return results

    async def sync_table(self, table_name: str) -> SyncResult:
        """Sync a specific table from Airtable to Supabase"""
        start_time = datetime.now(timezone.utc)
        table_config = self.mapping["tables"][table_name]

        logger.info(f"Starting sync for table: {table_name}")

        try:
            # Fetch data from Airtable
            airtable_records = await self._fetch_airtable_data(table_config)

            # Transform records
            transformed_records = []
            for record in airtable_records:
                try:
                    transformed = await self._transform_record(record, table_config)
                    if transformed:
                        transformed_records.append(transformed)
                except Exception as e:
                    logger.warning(
                        f"Failed to transform record {record.get('id', 'unknown')}: {e}"
                    )

            # Sync to Supabase
            result = await self._sync_to_supabase(table_config, transformed_records)

            # Update sync status
            await self._update_sync_status(table_name, len(transformed_records), True)

            result.duration_seconds = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds()
            logger.info(
                f"Completed sync for {table_name}: {result.records_processed} processed, "
                f"{result.records_created} created, {result.records_updated} updated"
            )

            return result

        except Exception as e:
            logger.error(f"Sync failed for table {table_name}: {e}")
            await self._update_sync_status(table_name, 0, False, str(e))
            raise

    async def _fetch_airtable_data(
        self, table_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Fetch data from Airtable"""
        base_id = self.mapping["base_id"]
        table_name = table_config["table"]
        view_name = table_config.get("view")

        url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
        headers = {
            "Authorization": f"Bearer {self.airtable_api_key}",
            "Content-Type": "application/json",
        }

        params = {}
        if view_name:
            params["view"] = view_name

        all_records = []
        offset = None

        while True:
            if offset:
                params["offset"] = offset

            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            records = data.get("records", [])
            all_records.extend(records)

            offset = data.get("offset")
            if not offset:
                break

            # Rate limiting
            await asyncio.sleep(
                1.0 / self.mapping["performance"]["rate_limit_requests_per_second"]
            )

        logger.info(
            f"Fetched {len(all_records)} records from Airtable table {table_name}"
        )
        return all_records

    async def _transform_record(
        self, airtable_record: Dict[str, Any], table_config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Transform Airtable record to Supabase format"""
        fields = airtable_record.get("fields", {})

        # Apply filters
        if not self._passes_filters(fields, table_config.get("filters", {})):
            return None

        transformed = {}

        # Transform mapped fields
        for supabase_field, field_config in table_config["fields"].items():
            airtable_field = field_config["airtable"]
            value = fields.get(airtable_field)

            # Apply default if value is None/empty
            if value is None or value == "":
                if "default" in field_config:
                    value = field_config["default"]
                elif field_config.get("required", False):
                    logger.warning(f"Required field {airtable_field} is missing")
                    return None

            # Apply transformations
            if value is not None:
                value = await self._apply_transformations(value, field_config)

                # Validate
                if not self._validate_field(value, field_config):
                    logger.warning(f"Field {supabase_field} failed validation: {value}")
                    if field_config.get("required", False):
                        return None

            transformed[supabase_field] = value

        # Add metadata
        metadata = {}
        for metadata_field in table_config.get("metadata_fields", []):
            if metadata_field in fields:
                metadata[metadata_field] = fields[metadata_field]

        if metadata:
            transformed["metadata"] = metadata

        # Add sync tracking fields
        transformed["airtable_record_id"] = airtable_record["id"]
        transformed["record_hash"] = self._compute_record_hash(fields)
        transformed["updated_at"] = datetime.now(timezone.utc).isoformat()

        return transformed

    def _passes_filters(self, fields: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if record passes configured filters"""
        for filter_field, filter_value in filters.items():
            field_value = fields.get(filter_field)

            if isinstance(filter_value, bool):
                # Boolean filter (e.g., publish: true)
                if bool(field_value) != filter_value:
                    return False
            elif isinstance(filter_value, str):
                # String exact match
                if field_value != filter_value:
                    return False
            elif isinstance(filter_value, list):
                # Value must be in list
                if field_value not in filter_value:
                    return False

        return True

    async def _apply_transformations(
        self, value: Any, field_config: Dict[str, Any]
    ) -> Any:
        """Apply field transformations"""
        if "transform" not in field_config:
            return value

        transform_name = field_config["transform"]
        transform_config = self.mapping["transformations"].get(transform_name, {})

        if transform_name == "lowercase_underscore":
            if isinstance(value, str):
                result = value.lower()
                for regex_rule in transform_config.get("regex", []):
                    result = re.sub(
                        regex_rule["pattern"], regex_rule["replace"], result
                    )
                return result

        elif transform_name == "lowercase":
            return value.lower() if isinstance(value, str) else value

        elif transform_name == "attachment_url":
            if isinstance(value, list) and len(value) > 0:
                return value[0].get("url")
            return None

        elif field_config.get("type") == "text_array":
            if isinstance(value, str):
                separator = field_config.get("separator", ",")
                return [item.strip() for item in value.split(separator) if item.strip()]
            return value

        elif field_config.get("type") == "json_array":
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return [value]
            return value if isinstance(value, list) else [value] if value else []

        return value

    def _validate_field(self, value: Any, field_config: Dict[str, Any]) -> bool:
        """Validate field value"""
        if value is None:
            return not field_config.get("required", False)

        # Check validation regex
        if "validation" in field_config and isinstance(value, str):
            if not re.match(field_config["validation"], value):
                return False

        # Check allowed values
        if "allowed_values" in field_config:
            if value not in field_config["allowed_values"]:
                return False

        # Check max length
        max_length = self.mapping["validation"].get("max_field_length", 10000)
        if isinstance(value, str) and len(value) > max_length:
            return False

        return True

    def _compute_record_hash(self, fields: Dict[str, Any]) -> str:
        """Compute hash for change detection"""
        # Sort fields for consistent hashing
        sorted_fields = json.dumps(fields, sort_keys=True, default=str)
        return hashlib.sha256(sorted_fields.encode()).hexdigest()

    async def _sync_to_supabase(
        self, table_config: Dict[str, Any], records: List[Dict[str, Any]]
    ) -> SyncResult:
        """Sync transformed records to Supabase"""
        table_name = table_config["supabase_table"]
        primary_key = table_config["primary_key"]

        result = SyncResult(table_name=table_name)
        result.records_processed = len(records)

        if not records:
            return result

        # Batch upsert records
        batch_size = self.mapping["sync_config"]["batch_size"]

        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]

            try:
                # Check which records need updates (hash-based change detection)
                existing_hashes = {}
                if self.mapping["sync_config"]["change_detection"] == "hash_based":
                    existing_records = (
                        self.supabase.table(table_name)
                        .select(f"{primary_key}, record_hash")
                        .in_(primary_key, [r[primary_key] for r in batch])
                        .execute()
                    )

                    existing_hashes = {
                        r[primary_key]: r["record_hash"] for r in existing_records.data
                    }

                # Separate creates and updates
                creates = []
                updates = []

                for record in batch:
                    pk_value = record[primary_key]
                    if pk_value in existing_hashes:
                        if existing_hashes[pk_value] != record["record_hash"]:
                            updates.append(record)
                    else:
                        creates.append(record)

                # Perform creates
                if creates:
                    self.supabase.table(table_name).insert(creates).execute()
                    result.records_created += len(creates)

                # Perform updates
                for record in updates:
                    self.supabase.table(table_name).update(record).eq(
                        primary_key, record[primary_key]
                    ).execute()
                    result.records_updated += 1

            except Exception as e:
                error_msg = f"Batch sync failed: {str(e)}"
                result.errors.append(error_msg)
                logger.error(error_msg)

        # Handle anchor relationships if this is the anchors table
        if table_name == "clausebot_anchors":
            await self._sync_anchor_relationships(records)

        return result

    async def _sync_anchor_relationships(self, anchor_records: List[Dict[str, Any]]):
        """Sync anchor-clause relationships"""
        try:
            # Clear existing relationships for these anchors
            anchor_names = [
                r["anchor_name"] for r in anchor_records if "anchor_name" in r
            ]
            if anchor_names:
                self.supabase.table("clause_anchor_links").delete().in_(
                    "anchor_name", anchor_names
                ).execute()

            # Insert new relationships
            links = []
            for record in anchor_records:
                anchor_name = record.get("anchor_name")
                related_clauses = record.get("related_clauses", [])

                if anchor_name and related_clauses:
                    for clause_ref in related_clauses:
                        links.append(
                            {
                                "anchor_name": anchor_name,
                                "clause_ref": clause_ref.strip(),
                                "link_strength": "primary",
                            }
                        )

            if links:
                self.supabase.table("clause_anchor_links").insert(links).execute()
                logger.info(f"Synced {len(links)} anchor-clause relationships")

        except Exception as e:
            logger.error(f"Failed to sync anchor relationships: {e}")

    async def _start_sync_job(self, job_type: str) -> str:
        """Start sync job tracking"""
        job_data = {
            "job_type": job_type,
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

        result = self.supabase.table("airtable_sync_jobs").insert(job_data).execute()
        return result.data[0]["job_id"]

    async def _complete_sync_job(self, job_id: str, results: Dict[str, SyncResult]):
        """Complete sync job tracking"""
        total_processed = sum(r.records_processed for r in results.values())
        total_created = sum(r.records_created for r in results.values())
        total_updated = sum(r.records_updated for r in results.values())

        update_data = {
            "status": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "records_processed": total_processed,
            "records_created": total_created,
            "records_updated": total_updated,
            "metadata": {"results": {k: v.__dict__ for k, v in results.items()}},
        }

        self.supabase.table("airtable_sync_jobs").update(update_data).eq(
            "job_id", job_id
        ).execute()

    async def _fail_sync_job(self, job_id: str, error_message: str):
        """Mark sync job as failed"""
        update_data = {
            "status": "failed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "error_message": error_message,
        }

        self.supabase.table("airtable_sync_jobs").update(update_data).eq(
            "job_id", job_id
        ).execute()

    async def _update_sync_status(
        self, table_name: str, record_count: int, success: bool, error: str = None
    ):
        """Update sync status for table"""
        now = datetime.now(timezone.utc).isoformat()

        update_data = {"last_sync_at": now, "total_records": record_count}

        if success:
            update_data["last_successful_sync_at"] = now
            update_data["sync_errors"] = 0
        else:
            update_data["sync_errors"] = 1
            if error:
                update_data["metadata"] = {"last_error": error}

        self.supabase.table("airtable_sync_status").upsert(
            {**update_data, "table_name": table_name}
        ).execute()


# Convenience functions for common operations
async def sync_all_tables() -> Dict[str, SyncResult]:
    """Sync all configured tables"""
    async with AirtableSyncService() as sync_service:
        return await sync_service.sync_all_tables()


async def sync_single_table(table_name: str) -> SyncResult:
    """Sync a single table"""
    async with AirtableSyncService() as sync_service:
        return await sync_service.sync_table(table_name)


async def get_sync_status() -> List[Dict[str, Any]]:
    """Get current sync status for all tables"""
    supabase = create_client(
        os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    )

    result = supabase.table("sync_dashboard").select("*").execute()
    return result.data
