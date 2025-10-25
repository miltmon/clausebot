#!/usr/bin/env python3
"""
ClauseBot Firebase Integration
Real-time incident tracking and team collaboration
Project: clausebot-v1-76670219
"""

import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Firebase project configuration
FIREBASE_PROJECT_ID = "clausebot-v1-76670219"
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
FIRESTORE_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"


class IncidentData(BaseModel):
    incident_id: str
    timestamp: str
    incident_type: str
    severity: str
    confidence: float
    system_context: Dict[str, Any]
    cursor_analysis: bool = True
    windsurf_cascade_required: bool = False


class ComplianceUpdate(BaseModel):
    update_id: str
    timestamp: str
    source: str
    webset_id: str
    title: str
    uri: str
    impact_severity: str
    confidence: float
    sections: list = []
    impact_tags: list = []


class FirebaseIntegration:
    """Firebase integration for real-time ClauseBot data"""

    def __init__(self, project_id: str = FIREBASE_PROJECT_ID):
        self.project_id = project_id
        self.base_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents"

    async def store_incident(self, incident: IncidentData) -> Optional[Dict]:
        """Store CURSOR incident in Firebase Firestore"""

        # Convert to Firestore document format
        firestore_doc = {
            "fields": {
                "incident_id": {"stringValue": incident.incident_id},
                "timestamp": {"timestampValue": incident.timestamp},
                "incident_type": {"stringValue": incident.incident_type},
                "severity": {"stringValue": incident.severity},
                "confidence": {"doubleValue": incident.confidence},
                "cursor_analysis": {"booleanValue": incident.cursor_analysis},
                "windsurf_cascade_required": {
                    "booleanValue": incident.windsurf_cascade_required
                },
                "system_context": {
                    "mapValue": {
                        "fields": {
                            key: {"stringValue": str(value)}
                            for key, value in incident.system_context.items()
                        }
                    }
                },
                "created_at": {
                    "timestampValue": datetime.now(timezone.utc).isoformat()
                },
                "status": {"stringValue": "active"},
                "team_notified": {"booleanValue": False},
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/incidents"
                async with session.post(url, json=firestore_doc) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Incident {incident.incident_id} stored in Firebase")
                        return result
                    else:
                        error_text = await response.text()
                        print(
                            f"❌ Firebase storage failed: {response.status} - {error_text}"
                        )
                        return None
        except Exception as e:
            print(f"❌ Firebase connection error: {str(e)}")
            return None

    async def store_compliance_update(self, update: ComplianceUpdate) -> Optional[Dict]:
        """Store Exa.ai compliance update in Firebase"""

        firestore_doc = {
            "fields": {
                "update_id": {"stringValue": update.update_id},
                "timestamp": {"timestampValue": update.timestamp},
                "source": {"stringValue": update.source},
                "webset_id": {"stringValue": update.webset_id},
                "title": {"stringValue": update.title},
                "uri": {"stringValue": update.uri},
                "impact_severity": {"stringValue": update.impact_severity},
                "confidence": {"doubleValue": update.confidence},
                "sections": {
                    "arrayValue": {
                        "values": [
                            {"stringValue": section} for section in update.sections
                        ]
                    }
                },
                "impact_tags": {
                    "arrayValue": {
                        "values": [{"stringValue": tag} for tag in update.impact_tags]
                    }
                },
                "created_at": {
                    "timestampValue": datetime.now(timezone.utc).isoformat()
                },
                "processed": {"booleanValue": False},
                "team_notified": {"booleanValue": False},
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/compliance_updates"
                async with session.post(url, json=firestore_doc) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(
                            f"✅ Compliance update {update.update_id} stored in Firebase"
                        )
                        return result
                    else:
                        error_text = await response.text()
                        print(
                            f"❌ Firebase storage failed: {response.status} - {error_text}"
                        )
                        return None
        except Exception as e:
            print(f"❌ Firebase connection error: {str(e)}")
            return None

    async def get_team_metrics(self) -> Optional[Dict]:
        """Retrieve real-time team metrics from Firebase"""

        try:
            async with aiohttp.ClientSession() as session:
                # Get recent incidents
                incidents_url = (
                    f"{self.base_url}/incidents?orderBy=timestamp desc&limitToFirst=10"
                )
                async with session.get(incidents_url) as response:
                    if response.status == 200:
                        incidents_data = await response.json()

                        # Get recent compliance updates
                        compliance_url = f"{self.base_url}/compliance_updates?orderBy=timestamp desc&limitToFirst=10"
                        async with session.get(compliance_url) as response:
                            if response.status == 200:
                                compliance_data = await response.json()

                                # Calculate metrics
                                metrics = {
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                    "incidents_24h": len(
                                        incidents_data.get("documents", [])
                                    ),
                                    "compliance_updates_24h": len(
                                        compliance_data.get("documents", [])
                                    ),
                                    "high_severity_incidents": 0,
                                    "pending_cascades": 0,
                                    "team_alerts_sent": 0,
                                    "system_health": "operational",
                                }

                                # Process incidents for detailed metrics
                                for doc in incidents_data.get("documents", []):
                                    fields = doc.get("fields", {})
                                    if (
                                        fields.get("severity", {}).get("stringValue")
                                        == "high"
                                    ):
                                        metrics["high_severity_incidents"] += 1
                                    if fields.get("windsurf_cascade_required", {}).get(
                                        "booleanValue"
                                    ):
                                        metrics["pending_cascades"] += 1

                                return metrics

                    return None
        except Exception as e:
            print(f"❌ Firebase metrics retrieval error: {str(e)}")
            return None

    async def update_incident_status(
        self, incident_id: str, status: str, cascade_result: Optional[Dict] = None
    ) -> bool:
        """Update incident status after Windsurf cascade completion"""

        update_fields = {
            "status": {"stringValue": status},
            "updated_at": {"timestampValue": datetime.now(timezone.utc).isoformat()},
        }

        if cascade_result:
            update_fields["cascade_result"] = {
                "mapValue": {
                    "fields": {
                        "cascade_id": {
                            "stringValue": cascade_result.get("cascade_id", "")
                        },
                        "result": {"stringValue": cascade_result.get("result", "")},
                        "latency_s": {
                            "doubleValue": cascade_result.get("latency_s", 0.0)
                        },
                        "steps_executed": {
                            "arrayValue": {
                                "values": [
                                    {"stringValue": step}
                                    for step in cascade_result.get("steps_executed", [])
                                ]
                            }
                        },
                    }
                }
            }

        try:
            async with aiohttp.ClientSession() as session:
                # First, find the document by incident_id
                query_url = f"{self.base_url}/incidents?where=incident_id={incident_id}"
                async with session.get(query_url) as response:
                    if response.status == 200:
                        query_result = await response.json()
                        documents = query_result.get("documents", [])

                        if documents:
                            doc_path = documents[0]["name"]
                            update_url = f"{doc_path}?updateMask.fieldPaths=status&updateMask.fieldPaths=updated_at"
                            if cascade_result:
                                update_url += "&updateMask.fieldPaths=cascade_result"

                            update_doc = {"fields": update_fields}

                            async with session.patch(
                                update_url, json=update_doc
                            ) as update_response:
                                if update_response.status == 200:
                                    print(
                                        f"✅ Incident {incident_id} status updated to {status}"
                                    )
                                    return True
                                else:
                                    error_text = await update_response.text()
                                    print(
                                        f"❌ Firebase update failed: {update_response.status} - {error_text}"
                                    )
                                    return False
                        else:
                            print(f"❌ Incident {incident_id} not found in Firebase")
                            return False
                    else:
                        error_text = await response.text()
                        print(
                            f"❌ Firebase query failed: {response.status} - {error_text}"
                        )
                        return False
        except Exception as e:
            print(f"❌ Firebase update error: {str(e)}")
            return False


# FastAPI integration
app = FastAPI()
firebase = FirebaseIntegration()


@app.post("/firebase/incident")
async def store_incident_endpoint(incident: IncidentData):
    """Store CURSOR incident in Firebase"""
    result = await firebase.store_incident(incident)
    if result:
        return {"status": "success", "firebase_doc": result["name"]}
    else:
        raise HTTPException(
            status_code=500, detail="Failed to store incident in Firebase"
        )


@app.post("/firebase/compliance")
async def store_compliance_endpoint(update: ComplianceUpdate):
    """Store compliance update in Firebase"""
    result = await firebase.store_compliance_update(update)
    if result:
        return {"status": "success", "firebase_doc": result["name"]}
    else:
        raise HTTPException(
            status_code=500, detail="Failed to store compliance update in Firebase"
        )


@app.get("/firebase/metrics")
async def get_metrics_endpoint():
    """Get real-time team metrics from Firebase"""
    metrics = await firebase.get_team_metrics()
    if metrics:
        return metrics
    else:
        raise HTTPException(
            status_code=500, detail="Failed to retrieve metrics from Firebase"
        )


@app.patch("/firebase/incident/{incident_id}/status")
async def update_incident_status_endpoint(
    incident_id: str, status: str, cascade_result: Optional[Dict] = None
):
    """Update incident status after Windsurf cascade"""
    success = await firebase.update_incident_status(incident_id, status, cascade_result)
    if success:
        return {"status": "success", "incident_id": incident_id, "new_status": status}
    else:
        raise HTTPException(status_code=500, detail="Failed to update incident status")


if __name__ == "__main__":
    import uvicorn

    print(f"🔥 Starting Firebase integration for project: {FIREBASE_PROJECT_ID}")
    uvicorn.run(app, host="0.0.0.0", port=8089)
