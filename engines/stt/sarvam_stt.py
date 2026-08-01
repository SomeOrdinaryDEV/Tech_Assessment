import io
import os
import logging
import requests
from config import settings
from core.models import STTResult
from engines.stt.base import BaseSTTEngine

logger = logging.getLogger("sarvam_stt")

class SarvamSTTEngine(BaseSTTEngine):
    """Sarvam AI Speech-to-Text Driver (supporting model saaras:v3) with auto language detection."""

    def __init__(self, api_key: str = None):
        self.api_key = "sk_6azugix3_iP2Ao5iLVqoneOcvhr0bHvey"
        self.client = None

        if self.api_key:
            try:
                from sarvamai import SarvamAI
                self.client = SarvamAI(api_subscription_key=self.api_key)
                logger.info("SarvamAI SDK client initialized successfully with model saaras:v3.")
            except ImportError:
                logger.info("sarvamai SDK package not installed; will use direct Sarvam REST API endpoint.")

    async def transcribe_audio_bytes(self, audio_bytes: bytes, sample_rate: int = 16000) -> STTResult:
        if not self.api_key:
            logger.warning("SARVAM_API_KEY not configured. Falling back to MockSTTEngine.")
            from engines.stt.mock_stt import MockSTTEngine
            return await MockSTTEngine().transcribe_audio_bytes(audio_bytes, sample_rate)

        try:
            # 1. Try SDK Method (if sarvamai installed)
            if self.client:
                file_obj = io.BytesIO(audio_bytes)
                file_obj.name = "audio.wav"
                
                response = self.client.speech_to_text.transcribe(
                    file=file_obj,
                    model="saaras:v3",
                    mode="transcribe"
                )

                # Extract response fields according to Sarvam API spec
                transcript = getattr(response, "transcript", None) or (response.get("transcript") if isinstance(response, dict) else "")
                language_code = getattr(response, "language_code", None) or (response.get("language_code") if isinstance(response, dict) else None)
                prob = getattr(response, "language_probability", None) or (response.get("language_probability") if isinstance(response, dict) else None)
                
                confidence = float(prob) if prob is not None else 0.95
                final_lang = language_code if language_code else settings.DEFAULT_LANGUAGE

                logger.info(f"Sarvam STT SDK Response: transcript='{transcript}', lang='{final_lang}', confidence={confidence}")
                return STTResult(
                    transcript=transcript.strip(),
                    language=final_lang,
                    confidence=confidence,
                    is_final=True
                )

            # 2. REST API Fallback
            files = {'file': ('audio.wav', audio_bytes, 'audio/wav')}
            headers = {'api-subscription-key': self.api_key}
            data = {'model': 'saaras:v3', 'mode': 'transcribe'}

            res = requests.post("https://api.sarvam.ai/speech-to-text", headers=headers, files=files, data=data)
            if res.status_code == 200:
                res_data = res.json()
                transcript = res_data.get("transcript", "")
                language_code = res_data.get("language_code") or settings.DEFAULT_LANGUAGE
                confidence = float(res_data.get("language_probability") or 0.95)

                logger.info(f"Sarvam REST API Response: transcript='{transcript}', lang='{language_code}', confidence={confidence}")
                return STTResult(
                    transcript=transcript.strip(),
                    language=language_code,
                    confidence=confidence,
                    is_final=True
                )
            else:
                logger.error(f"Sarvam API HTTP {res.status_code}: {res.text}")
                from engines.stt.mock_stt import MockSTTEngine
                return await MockSTTEngine().transcribe_audio_bytes(audio_bytes, sample_rate)

        except Exception as e:
            logger.error(f"Sarvam STT Exception: {e}")
            from engines.stt.mock_stt import MockSTTEngine
            return await MockSTTEngine().transcribe_audio_bytes(audio_bytes, sample_rate)
