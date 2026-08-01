import json
import logging
from typing import List
from fastapi import WebSocket
from core.models import EscalationPayload

logger = logging.getLogger("teleconsult_portal")

class TeleconsultPortalManager:
    """Real-time WebSocket Manager for broadcasting red-flag emergency escalations to duty clinicians."""

    def __init__(self):
        self.active_clinicians: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_clinicians.append(websocket)
        logger.info(f"Clinician connected to Teleconsultation Portal. Active doctors: {len(self.active_clinicians)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_clinicians:
            self.active_clinicians.remove(websocket)
            logger.info(f"Clinician disconnected. Remaining doctors: {len(self.active_clinicians)}")

    async def broadcast_escalation(self, payload: EscalationPayload):
        """Broadcasts emergency red flag notification to all connected clinician dashboards."""
        if not self.active_clinicians:
            logger.warning(f"EMERGENCY ESCALATION TRIGGERED but no clinicians currently connected! Payload: {payload.dict()}")
            return

        json_msg = payload.json()
        disconnected = []

        for websocket in self.active_clinicians:
            try:
                await websocket.send_text(json_msg)
                logger.info(f"Broadcasted red flag alert to clinician WebSocket.")
            except Exception as e:
                logger.error(f"Failed sending alert to clinician: {e}")
                disconnected.append(websocket)

        for ws in disconnected:
            self.disconnect(ws)

teleconsult_portal = TeleconsultPortalManager()
