from abc import ABC, abstractmethod
from core.models import STTResult

class BaseSTTEngine(ABC):
    """Abstract Base Class for Speech-To-Text Drivers"""

    @abstractmethod
    async def transcribe_audio_bytes(self, audio_bytes: bytes, sample_rate: int = 16000) -> STTResult:
        """Converts audio bytes into transcribed text and detected language tag."""
        pass
