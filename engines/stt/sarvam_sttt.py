import io
import os
import logging
import requests
from config import settings
from sarvamai import SarvamAI
from core.models import STTResult
from engines.stt.base import BaseSTTEngine

logger = logging.getLogger("sarvam_stt")

class SarvamSTTEngine(BaseSTTEngine):
    """Sarvam AI Speech-to-Text Driver and translator (supporting model saaras:v3) with auto language detection."""

    def __init__(self, api_key: str = None):
        # NOTE: It is highly recommended to fetch this from env vars, e.g., os.getenv("SARVAM_API_KEY")
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
                
                # Call 1: Transcribe
                transcribe_response = self.client.speech_to_text.transcribe(
                    file=file_obj,
                    model="saaras:v3",
                    mode="transcribe"
                )
                
                # Reset the file stream pointer to the beginning for the second call
                file_obj.seek(0)
                
                # Call 2: Translate
                translate_response = self.client.speech_to_text.transcribe(
                    file=file_obj,
                    model="saaras:v3",
                    mode="translate"
                )

                # Extract response fields according to Sarvam API spec
                # For transcription
                transcript = getattr(transcribe_response, "transcript", None) or (transcribe_response.get("transcript") if isinstance(transcribe_response, dict) else "")
                language_code = getattr(transcribe_response, "language_code", None) or (transcribe_response.get("language_code") if isinstance(transcribe_response, dict) else None)
                prob = getattr(transcribe_response, "language_probability", None) or (transcribe_response.get("language_probability") if isinstance(transcribe_response, dict) else None)
                
                # For translation
                translation = getattr(translate_response, "transcript", None) or (translate_response.get("transcript") if isinstance(translate_response, dict) else "")

                confidence = float(prob) if prob is not None else 0.95
                final_lang = language_code if language_code else settings.DEFAULT_LANGUAGE

                logger.info(f"Sarvam STT SDK Response: transcript='{transcript}', translation='{translation}', lang='{final_lang}', confidence={confidence}")
                
                return STTResult(
                    transcript=transcript.strip(),
                    translation=translation.strip(), 
                    language=final_lang,
                    confidence=confidence,
                    is_final=True
                )

            # 2. REST API Fallback
            headers = {'api-subscription-key': self.api_key}
            
            # Call 1: Transcribe
            files_transcribe = {'file': ('audio.wav', audio_bytes, 'audio/wav')}
            data_transcribe = {'model': 'saaras:v3', 'mode': 'transcribe'}
            res_transcribe = requests.post("https://api.sarvam.ai/speech-to-text", headers=headers, files=files_transcribe, data=data_transcribe)
            
            # Call 2: Translate (We recreate the 'files' dict so it starts from fresh bytes)
            files_translate = {'file': ('audio.wav', audio_bytes, 'audio/wav')}
            data_translate = {'model': 'saaras:v3', 'mode': 'translate'}
            res_translate = requests.post("https://api.sarvam.ai/speech-to-text", headers=headers, files=files_translate, data=data_translate)

            if res_transcribe.status_code == 200 and res_translate.status_code == 200:
                transcribe_data = res_transcribe.json()
                translate_data = res_translate.json()

                transcript = transcribe_data.get("transcript", "")
                translation = translate_data.get("transcript", "")
                language_code = transcribe_data.get("language_code") or settings.DEFAULT_LANGUAGE
                confidence = float(transcribe_data.get("language_probability") or 0.95)

                logger.info(f"Sarvam REST API Response: transcript='{transcript}', translation='{translation}', lang='{language_code}', confidence={confidence}")
                
                return STTResult(
                    transcript=transcript.strip(),
                    translation=translation.strip(), # Ensure your STTResult model accepts this field
                    language=language_code,
                    confidence=confidence,
                    is_final=True
                )
            else:
                logger.error(f"Sarvam API HTTP Error. Transcribe Status: {res_transcribe.status_code}, Translate Status: {res_translate.status_code}")
                from engines.stt.mock_stt import MockSTTEngine
                return await MockSTTEngine().transcribe_audio_bytes(audio_bytes, sample_rate)

        except Exception as e:
            logger.error(f"Sarvam STT Exception: {e}")
            from engines.stt.mock_stt import MockSTTEngine
            return await MockSTTEngine().transcribe_audio_bytes(audio_bytes, sample_rate)