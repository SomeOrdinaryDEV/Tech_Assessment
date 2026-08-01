import base64
import logging
from typing import Optional
from engines.tts.base import BaseTTSEngine

logger = logging.getLogger("mock_tts")

class MockTTSEngine(BaseTTSEngine):
    """Mock TTS driver generating a lightweight valid audio payload for testing."""

    async def synthesize_speech(self, text: str, language: str = "hi-IN") -> Optional[str]:
        if not text:
            return None
            
        # Minimal silent/beep MP3 audio payload encoded in base64
        # Allows Web Audio API in frontend to play without throwing errors when offline
        dummy_mp3 = (
            b"\xff\xf3\x44\xc4\x00\x00\x00\x03\x48\x00\x00\x00\x00"
            b"\x4c\x41\x4d\x45\x33\x2e\x39\x39\x2e\x35\x00\x00\x00"
        ) * 50
        
        logger.info(f"Mock TTS generated audio response for language '{language}'. Text length: {len(text)}")
        return base64.b64encode(dummy_mp3).decode("utf-8")
