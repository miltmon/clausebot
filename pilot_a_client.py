#!/usr/bin/env python3
"""
Pilot A API Client - Integration bridge between local diagnostics and ClauseBot API
Connects CURSOR incident analysis and Windsurf cascade execution to production API
"""

import requests
from typing import Dict, Any, Optional
import os


class PilotAClient:
    def __init__(self, base_url: str = "http://localhost:8081", api_key: str = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("CLAUSEBOT_API_KEY", "dev-key-pilot-a")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def analyze_incident(
        self,
        trigger: str,
        system_context: Dict[str, Any],
        chrome_memory_mb: Optional[int] = None,
        gpu_driver_version: Optional[str] = None,
        free_ram_gb: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        CURSOR Incident Analysis via API
        """
        payload = {
            "trigger": trigger,
            "system_context": system_context,
            "chrome_memory_mb": chrome_memory_mb,
            "gpu_driver_version": gpu_driver_version,
            "free_ram_gb": free_ram_gb,
            "confidence_threshold": 0.8,
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/pilot-a/incidents/analyze",
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ Incident analysis API error: {e}")
            return {"error": str(e)}

    def execute_cascade(
        self,
        incident_id: str,
        cascade_type: str = "reset-validate",
        namespace: str = "test-ns",
    ) -> Dict[str, Any]:
        """
        Windsurf Cascade Execution via API
        """
        payload = {
            "incident_id": incident_id,
            "cascade_type": cascade_type,
            "namespace": namespace,
            "approval_gate": "hitl_required",
            "rollback_on_fail": True,
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/pilot-a/cascades/execute",
                headers=self.headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ Cascade execution API error: {e}")
            return {"error": str(e)}

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get Pilot A unified metrics
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/pilot-a/metrics",
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ Metrics API error: {e}")
            return {"error": str(e)}

    def health_check(self) -> Dict[str, Any]:
        """
        Check Pilot A system health
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/pilot-a/health",
                headers=self.headers,
                timeout=5,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ Health check API error: {e}")
            return {"error": str(e)}


def demo_pilot_a_workflow():
    """
    Demonstrate complete Pilot A workflow via API
    """
    print("🌊 Pilot A API Integration Demo")
    print("=" * 40)

    client = PilotAClient()

    # 1. Health Check
    print("1. 🔍 Health Check...")
    health = client.health_check()
    if "error" not in health:
        print(f"   ✅ Status: {health['status']}")
        print(
            f"   📊 Components: {health['components']['cursor_engine']}, {health['components']['windsurf_cascades']}"
        )
    else:
        print(f"   ❌ Health check failed: {health['error']}")
        return

    # 2. CURSOR Incident Analysis
    print("\n2. 🔍 CURSOR Incident Analysis...")
    incident_analysis = client.analyze_incident(
        trigger="chrome_hung",
        system_context={"intel_ultra_7": True, "windows_11": True},
        chrome_memory_mb=1832,
        gpu_driver_version="31.0.101.4826",
        free_ram_gb=1.8,
    )

    if "error" not in incident_analysis:
        print(f"   ✅ Incident ID: {incident_analysis['incident_id']}")
        print(
            f"   🎯 Root Cause: {incident_analysis['root_cause']} (confidence: {incident_analysis['confidence']})"
        )
        print(f"   🔧 Proposed Fix: {incident_analysis['proposed_fix']}")
        print(
            f"   🌊 Windsurf Handoff: {incident_analysis['windsurf_handoff_required']}"
        )
    else:
        print(f"   ❌ Analysis failed: {incident_analysis['error']}")
        return

    # 3. Windsurf Cascade Execution
    if incident_analysis.get("windsurf_handoff_required"):
        print("\n3. 🌊 Windsurf Cascade Execution...")
        cascade_result = client.execute_cascade(
            incident_id=incident_analysis["incident_id"],
            cascade_type="reset-validate",
            namespace="test-ns",
        )

        if "error" not in cascade_result:
            print(f"   ✅ Cascade ID: {cascade_result['cascade_id']}")
            print(
                f"   ⚡ Result: {cascade_result['result']} ({cascade_result['latency_s']}s)"
            )
            print(
                f"   📈 MTTR Improvement: {cascade_result['mttr_contribution']['improvement_pct'] * 100:.1f}%"
            )
            print(f"   📋 Steps: {' → '.join(cascade_result['steps_executed'])}")
        else:
            print(f"   ❌ Cascade failed: {cascade_result['error']}")

    # 4. Unified Metrics
    print("\n4. 📊 Unified Metrics...")
    metrics = client.get_metrics()
    if "error" not in metrics:
        cursor = metrics["cursor_metrics"]
        windsurf = metrics["windsurf_metrics"]
        unified = metrics["unified_metrics"]

        print(
            f"   🔍 CURSOR: {cursor['incidents_detected']} incidents, {cursor['precision']:.2f} precision"
        )
        print(
            f"   🌊 Windsurf: {windsurf['cascade_executions']} cascades, {windsurf['success_rate']:.2f} success rate"
        )
        print(
            f"   🎯 MTTR: {unified['mttr_baseline_s']}s → {unified['mttr_observed_s']}s ({unified['mttr_delta_pct'] * 100:.1f}% improvement)"
        )

        # Success criteria
        criteria = metrics["success_criteria"]
        all_met = all(criteria.values())
        print(f"   🏆 Success Criteria: {'✅ ALL MET' if all_met else '⚠️  PARTIAL'}")
    else:
        print(f"   ❌ Metrics failed: {metrics['error']}")

    print("\n🎯 Pilot A API Integration Demo Complete!")


if __name__ == "__main__":
    demo_pilot_a_workflow()
