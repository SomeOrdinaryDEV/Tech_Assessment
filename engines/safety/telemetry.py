import logging
import time
from typing import Dict, Any

logger = logging.getLogger("safety_telemetry")

class SafetyTelemetryTracker:
    """Audit logger tracking safety gate triggers, missed escalations, and latency metrics."""

    def __init__(self):
        self.total_queries = 0
        self.emergency_triggers = 0
        self.rejections = 0
        self.logs = []

    def log_event(self, session_id: str, transcript: str, is_emergency: bool, red_flag: str, latency_ms: float):
        self.total_queries += 1
        if is_emergency:
            self.emergency_triggers += 1

        event = {
            "timestamp": time.time(),
            "session_id": session_id,
            "transcript": transcript,
            "is_emergency": is_emergency,
            "red_flag": red_flag,
            "latency_ms": latency_ms
        }
        self.logs.append(event)
        logger.info(f"Telemetry Audit Event: session={session_id}, emergency={is_emergency}, latency={latency_ms:.2f}ms")

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "total_queries": self.total_queries,
            "emergency_triggers": self.emergency_triggers,
            "rejections": self.rejections,
            "emergency_rate_pct": (self.emergency_triggers / max(1, self.total_queries)) * 100
        }

telemetry_tracker = SafetyTelemetryTracker()
