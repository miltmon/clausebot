import hashlib
import json
import os
from typing import Dict, Any
from datetime import datetime
import threading


class ContentIntegrityManager:
    def __init__(self, content_dir: str = "./data"):
        self.content_dir = content_dir
        self.manifest_file = os.path.join(
            content_dir, "codes/aws_d1_1_2020/manifest.json"
        )
        self.index_dir = os.path.join(content_dir, "codes/aws_d1_1_2020/index")
        self.lock = threading.Lock()
        self._load_manifest()

    def _load_manifest(self):
        """Load manifest from file"""
        if os.path.exists(self.manifest_file):
            with open(self.manifest_file, "r", encoding="utf-8") as f:
                self.manifest = json.load(f)
        else:
            self.manifest = {
                "edition": "AWS_D1.1:2025",
                "timestamp": datetime.utcnow().isoformat(),
                "files": [],
                "integrity_checks": {
                    "last_verified": None,
                    "verification_status": "pending",
                    "checksum_valid": False,
                },
            }

    def _save_manifest(self):
        """Save manifest to file"""
        with self.lock:
            with open(self.manifest_file, "w", encoding="utf-8") as f:
                json.dump(self.manifest, f, indent=2, ensure_ascii=False)

    def verify_checksums(self) -> Dict[str, Any]:
        """Verify all file checksums against manifest"""
        verification_result = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "files_checked": 0,
            "files_valid": 0,
            "files_invalid": 0,
            "errors": [],
        }

        try:
            for file_info in self.manifest.get("files", []):
                file_path = os.path.join(
                    self.content_dir,
                    "codes/aws_d1_1_2020/source_pdfs",
                    file_info["file"],
                )
                verification_result["files_checked"] += 1

                if os.path.exists(file_path):
                    # Calculate current checksum
                    with open(file_path, "rb") as f:
                        current_hash = hashlib.sha256(f.read()).hexdigest().lower()

                    # Compare with stored checksum
                    if current_hash == file_info["sha256"]:
                        verification_result["files_valid"] += 1
                    else:
                        verification_result["files_invalid"] += 1
                        verification_result["errors"].append(
                            {
                                "file": file_info["file"],
                                "expected": file_info["sha256"],
                                "actual": current_hash,
                                "error": "checksum_mismatch",
                            }
                        )
                else:
                    verification_result["files_invalid"] += 1
                    verification_result["errors"].append(
                        {"file": file_info["file"], "error": "file_not_found"}
                    )

            # Update manifest with verification results
            self.manifest["integrity_checks"] = {
                "last_verified": verification_result["timestamp"],
                "verification_status": (
                    "success" if verification_result["files_invalid"] == 0 else "failed"
                ),
                "checksum_valid": verification_result["files_invalid"] == 0,
            }

            if verification_result["files_invalid"] > 0:
                verification_result["status"] = "failed"

            self._save_manifest()

        except Exception as e:
            verification_result["status"] = "error"
            verification_result["errors"].append(
                {"error": "verification_exception", "message": str(e)}
            )

        return verification_result

    def get_edition_info(self) -> Dict[str, Any]:
        """Get current edition information"""
        return {
            "edition": self.manifest.get("edition", "AWS_D1.1:2025"),
            "timestamp": self.manifest.get("timestamp"),
            "files_count": len(self.manifest.get("files", [])),
            "last_verified": self.manifest.get("integrity_checks", {}).get(
                "last_verified"
            ),
            "verification_status": self.manifest.get("integrity_checks", {}).get(
                "verification_status", "pending"
            ),
            "checksum_valid": self.manifest.get("integrity_checks", {}).get(
                "checksum_valid", False
            ),
        }

    def validate_edition_request(self, requested_edition: str) -> bool:
        """Validate if requested edition is allowed"""
        current_edition = self.manifest.get("edition", "AWS_D1.1:2025")

        # For now, only allow current edition
        # In future, can support multiple editions
        return requested_edition == current_edition

    def generate_content_checksum(self, code: str, clause: str, edition: str) -> str:
        """Generate content checksum for a specific clause"""
        content_string = (
            f"{code}:{clause}:{edition}:{self.manifest.get('timestamp', '')}"
        )
        return f"sha256:{hashlib.sha256(content_string.encode()).hexdigest()[:8]}"

    def check_index_integrity(self) -> Dict[str, Any]:
        """Check if index files are present and valid"""
        index_check = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "files_checked": 0,
            "files_valid": 0,
            "files_missing": 0,
            "errors": [],
        }

        required_files = ["index.json", "clauses.json"]

        for filename in required_files:
            file_path = os.path.join(self.index_dir, filename)
            index_check["files_checked"] += 1

            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        json.load(f)  # Validate JSON
                    index_check["files_valid"] += 1
                except json.JSONDecodeError as e:
                    index_check["errors"].append(
                        {"file": filename, "error": "invalid_json", "message": str(e)}
                    )
            else:
                index_check["files_missing"] += 1
                index_check["errors"].append(
                    {"file": filename, "error": "file_missing"}
                )

        if index_check["files_missing"] > 0 or index_check["errors"]:
            index_check["status"] = "failed"

        return index_check

    def schedule_nightly_verification(self):
        """Schedule nightly verification job (placeholder for cron job)"""
        # In production, this would be a scheduled job
        # For now, just log that it should be scheduled
        print("NIGHTLY_VERIFICATION: Should be scheduled via cron or task scheduler")
        print(
            "Command: python -c 'from api.content_integrity import ContentIntegrityManager; cm = ContentIntegrityManager(); cm.verify_checksums()'"
        )


# Global content integrity manager
content_manager = ContentIntegrityManager()


def get_edition_guard(edition: str = None) -> str:
    """Get edition with validation"""
    if edition and not content_manager.validate_edition_request(edition):
        raise ValueError(
            f"Edition {edition} not supported. Current edition: {content_manager.get_edition_info()['edition']}"
        )

    return edition or content_manager.get_edition_info()["edition"]


def generate_clause_checksum(code: str, clause: str, edition: str = None) -> str:
    """Generate checksum for clause response"""
    validated_edition = get_edition_guard(edition)
    return content_manager.generate_content_checksum(code, clause, validated_edition)
