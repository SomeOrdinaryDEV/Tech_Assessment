import base64
import logging
from typing import Optional
from config import settings
from engines.tts.base import BaseTTSEngine

logger = logging.getLogger("google_tts")

class GoogleTTSEngine(BaseTTSEngine):
    def __init__(self):
        self.client = None
        try:
            from google.cloud import texttospeech
            self.tts_module = texttospeech
            self.client = texttospeech.TextToSpeechClient()
            logger.info("Google Cloud TTS client initialized successfully.")
        except Exception as e:
            logger.warning(f"Google Cloud TTS SDK not configured or credentials missing: {e}. Will fallback to mock mode.")

    async def synthesize_speech(self, text: str, language: str = "hi-IN") -> Optional[str]:
        if not self.client or not text:
            from engines.tts.mock_tts import MockTTSEngine
            return await MockTTSEngine().synthesize_speech(text, language)

        try:
            input_text = self.tts_module.SynthesisInput(text=text)
            voice = self.tts_module.VoiceSelectionParams(
                language_code=language,
                ssml_gender=self.tts_module.SsmlVoiceGender.FEMALE
            )
            audio_config = self.tts_module.AudioConfig(
                audio_encoding=self.tts_module.AudioEncoding.MP3
            )

            response = self.client.synthesize_speech(
                input=input_text, voice=voice, audio_config=audio_config
            )
            return base64.b64encode(response.audio_content).decode("utf-8")
        except Exception as e:
            logger.error(f"Error synthesizing speech via Google TTS: {e}")
            from engines.tts.mock_tts import MockTTSEngine
            return await MockTTSEngine().synthesize_speech(text, language)
