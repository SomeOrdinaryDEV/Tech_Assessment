from abc import ABC, abstractmethod
from typing import Optional

class BaseTTSEngine(ABC):
    """Abstract Base Class for Text-To-Speech Drivers"""

    @abstractmethod
    async def synthesize_speech(self, text: str, language: str = "hi-IN") -> Optional[str]:
        """Synthesizes text into base64 encoded MP3/WAV audio string."""
        pass
