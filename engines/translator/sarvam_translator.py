import re
import logging
import requests
from config import settings

logger = logging.getLogger("sarvam_translator")

INDIC_UNICODE_PATTERN = re.compile(r'[\u0900-\u0D7F]')

class SarvamTranslatorEngine:
    """Translation Engine converting native Indic script (e.g., Devanagari 'भारत') to English/Hinglish ('Bharat') for vector searching."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.SARVAM_API_KEY
        self.client = None

        if self.api_key:
            try:
                from sarvamai import SarvamAI
                self.client = SarvamAI(api_subscription_key=self.api_key)
                logger.info("SarvamAI Translator SDK client initialized.")
            except ImportError:
                logger.info("sarvamai SDK not installed; using direct Sarvam Translate REST API endpoint.")

    def is_indic_script(self, text: str) -> bool:
        """Detects if text contains native Indic script characters (Devanagari, Tamil, Telugu, Malayalam, Kannada)."""
        return bool(INDIC_UNICODE_PATTERN.search(text))

    async def translate_to_english(self, text: str, source_language_code: str = "hi-IN") -> str:
        """Translates native Indic script text to English for vector matching."""
        if not text or not self.is_indic_script(text):
            # Already in Latin / Hinglish script
            return text

        if not self.api_key:
            logger.warning("SARVAM_API_KEY missing. Applying fallback transliteration dictionary.")
            return self._fallback_transliterate(text)

        try:
            # 1. SDK Method
            if self.client:
                response = self.client.text_translation.translate(
                    input=text,
                    source_language_code=source_language_code,
                    target_language_code="en-IN",
                    model="mayura:v1"
                )
                translated_text = getattr(response, "translated_text", "") or (response.get("translated_text") if isinstance(response, dict) else "")
                if translated_text:
                    logger.info(f"Sarvam Translate: '{text}' -> '{translated_text}'")
                    return translated_text.strip()

            # 2. REST API Method
            headers = {
                'api-subscription-key': self.api_key,
                'Content-Type': 'application/json'
            }
            payload = {
                "input": text,
                "source_language_code": source_language_code,
                "target_language_code": "en-IN",
                "model": "mayura:v1"
            }
            res = requests.post("https://api.sarvam.ai/translate", headers=headers, json=payload)
            if res.status_code == 200:
                res_data = res.json()
                translated = res_data.get("translated_text", "")
                if translated:
                    logger.info(f"Sarvam REST Translate: '{text}' -> '{translated}'")
                    return translated.strip()

        except Exception as e:
            logger.error(f"Sarvam Translation error: {e}")

        return self._fallback_transliterate(text)

    def _fallback_transliterate(self, text: str) -> str:
        """Dictionary transliterator fallback for key health & scheme terms."""
        mapping = {
            "भारत": "Bharat",
            "आयुष्मान": "Ayushman",
            "अस्पताल": "hospital", "மருத்துவமனை": "hospital", "ఆసుపత్రి": "hospital",
            "दवा": "dawa medicine tablet", "மருந்து": "medicine", "మందు": "medicine",
            "बुखार": "fever", "காய்ச்சல்": "fever", "జ్వరం": "fever",
            "खांसी": "cough", "இருமல்": "cough",
            "दर्द": "pain", "வலி": "pain", "నొప్పి": "pain",
            "सीने में दर्द": "chest pain", "நெஞ்சு வலி": "chest pain", "గుండె నొప్పి": "chest pain",
            "सांस": "breath", "மூச்சு": "breath", "శ్వాస": "breath",
            "सरकारी": "sarkari government", "फ्री": "free", "योजना": "yojana scheme"
        }

        result = text
        for native_word, english_word in mapping.items():
            result = result.replace(native_word, english_word)

        return result
