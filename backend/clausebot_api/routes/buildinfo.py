"""Build information endpoint for deployment verification."""
from __future__ import annotations
from typing import Dict, Any
from pathlib import Path
from fastapi import APIRouter

router = APIRouter()


def _read_buildinfo() -> Dict[str, Any]:
    """Read build information from buildinfo.txt if it exists."""
    buildinfo_path = Path(__file__).resolve().parents[2] / "buildinfo.txt"
    
    if buildinfo_path.exists():
        info = {}
        for line in buildinfo_path.read_text().splitlines():
            if "=" in line:
                key, value = line.strip().split("=", 1)
                info[key] = value
        return info
    
    # Fallback if buildinfo.txt doesn't exist
    return {
        "REPO": "unknown",
        "SHA": "unknown", 
        "DATE": "unknown",
        "note": "buildinfo.txt not found - run CI/CD build to generate"
    }


@router.get("/buildinfo")
def get_buildinfo() -> Dict[str, Any]:
    """
    Returns build information including repository, commit SHA, and build date.
    
    This endpoint provides definitive proof of what code is currently deployed,
    eliminating any guesswork about which repository or commit is live.
    """
    return _read_buildinfo()

