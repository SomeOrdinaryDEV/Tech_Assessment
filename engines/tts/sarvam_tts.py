import base64
import io
import logging
from sarvamai import SarvamAI

logger = logging.getLogger("sarvam_tts")

class SarvamTTSEngine:
    def __init__(self, api_key: str):
        self.client = SarvamAI(api_subscription_key=api_key)

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text if necessary. Returns the original text if target is English."""
        if target_lang == "en-IN" or not text:
            return text
        try:
            response = self.client.text.translate(
                source_language_code="en-IN",   # RAG always returns English
                input=text,
                target_language_code=target_lang,
                model="mayura:v1",
                numerals_format="international",
                mode="formal",
            )
            logger.info(f"Translated to {target_lang}")
            return response.translated_text
        except Exception as e:
            logger.warning(f"Translation failed: {e}. Falling back to English.")
            return text

    def generate_audio(self, text: str, language: str) -> bytes:
        """Generate speech audio and return raw MP3 bytes."""
        if not text:
            return b""
        # Determine target language code (SarvamAI expects e.g. "hi-IN")
        target_lang = language if language else "hi-IN"
        try:
            audio_stream = self.client.text_to_speech.convert_stream(
                text=text,
                target_language_code=target_lang,
                speaker="shubh",
                model="bulbul:v3",
                pace=0.77,
                speech_sample_rate=22050,
            )
            # Collect chunks into a bytes buffer
            buffer = io.BytesIO()
            for chunk in audio_stream:
                if chunk:
                    buffer.write(chunk)
            audio_bytes = buffer.getvalue()
            logger.info(f"Generated {len(audio_bytes)} bytes of audio")
            return audio_bytes
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return b""

    async def synthesize_speech(self, text: str, language: str) -> str:
        """
        Full pipeline: translate (if needed) → TTS → base64 encoded audio.
        Returns a base64 string usable in the pipeline.
        """
        # 1. Translate (RAG output is English, user's language may differ)
        translated_text = self.translate(text, source_lang="en-IN", target_lang=language)

        # 2. Generate raw audio bytes
        audio_bytes = self.generate_audio(translated_text, language)

        if not audio_bytes:
            logger.warning("No audio generated. Returning empty base64.")
            return ""

        # 3. Base64 encode
        b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
        return b64_audio