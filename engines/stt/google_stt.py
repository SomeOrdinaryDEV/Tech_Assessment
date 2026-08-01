import logging
from config import settings
from core.models import STTResult
from engines.stt.base import BaseSTTEngine

logger = logging.getLogger("google_stt")

class GoogleSTTEngine(BaseSTTEngine):
    def __init__(self):
        self.supported_langs = settings.SUPPORTED_LANGUAGES
        self.client = None
        
        # Try initializing Google Cloud Speech client if credentials present
        try:
            from google.cloud import speech
            self.speech_module = speech
            self.client = speech.SpeechClient()
            logger.info("Google Cloud Speech client initialized successfully.")
        except Exception as e:
            logger.warning(f"Google Cloud Speech SDK not configured or credentials missing: {e}. Will fallback to mock mode.")

    async def transcribe_audio_bytes(self, audio_bytes: bytes, sample_rate: int = 16000) -> STTResult:
        if not self.client:
            # Fallback to internal simulation if SDK missing
            from engines.stt.mock_stt import MockSTTEngine
            return await MockSTTEngine().transcribe_audio_bytes(audio_bytes, sample_rate)

        try:
            audio = self.speech_module.RecognitionAudio(content=audio_bytes)
            config = self.speech_module.RecognitionConfig(
                encoding=self.speech_module.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=sample_rate,
                language_code=settings.DEFAULT_LANGUAGE,
                alternative_language_codes=[lang for lang in settings.SUPPORTED_LANGUAGES if lang != settings.DEFAULT_LANGUAGE],
                enable_automatic_punctuation=True,
            )

            response = self.client.recognize(config=config, audio=audio)
            if not response.results:
                return STTResult(transcript="", language=settings.DEFAULT_LANGUAGE, confidence=0.0, is_final=True)

            result = response.results[0]
            alternative = result.alternatives[0]
            detected_lang = result.language_code if result.language_code else settings.DEFAULT_LANGUAGE

            return STTResult(
                transcript=alternative.transcript.strip(),
                language=detected_lang,
                confidence=float(alternative.confidence),
                is_final=True
            )
        except Exception as e:
            logger.error(f"Error in Google STT transcription: {e}")
            from engines.stt.mock_stt import MockSTTEngine
            return await MockSTTEngine().transcribe_audio_bytes(audio_bytes, sample_rate)
