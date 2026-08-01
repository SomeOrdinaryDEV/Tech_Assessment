import random
from core.models import STTResult
from engines.stt.base import BaseSTTEngine

class MockSTTEngine(BaseSTTEngine):
    """Mock STT driver for local testing and offline execution."""
    
    def __init__(self):
        self.sample_queries = [
            # Adherence queries
            ("Mera TB ka dawa miss ho gaya, kya karu?", "hi-IN"),
            ("Naan innaikku tablet miss pannitten, enna seiyyanum?", "ta-IN"),
            ("Nenu ee roju tablet vesukoledhu, em cheyali?", "te-IN"),
            
            # Schemes queries
            ("Ayushman Bharat card se konsa hospital free hai?", "hi-IN"),
            ("Ayushman card-il ethenkilum hospital free aano?", "ml-IN"),
            ("Ayushman card ninda yavudhu hospital free ide?", "kn-IN"),
            
            # Facility Linkage queries
            ("Mere paas ka PHC ya sarkari hospital kahan hai?", "hi-IN"),
            ("Kittiyirukkum PHC alladhu maruthuvamanai enge irukkiradhu?", "ta-IN"),
            
            # Triage queries
            ("Mujhe 3 din se bukhar hai aur khansi aa rahi hai", "hi-IN"),
            ("Mera seene me bahut tej dard ho raha hai aur saans nahi aa rahi", "hi-IN"),  # Red flag emergency
        ]

    async def transcribe_audio_bytes(self, audio_bytes: bytes, sample_rate: int = 16000) -> STTResult:
        # If payload is empty
        if not audio_bytes:
            return STTResult(transcript="", language="hi-IN", confidence=0.0, is_final=True)
            
        # If text bytes are passed directly in tests, decode directly
        try:
            decoded = audio_bytes.decode("utf-8").strip()
            if decoded and len(decoded) > 3:
                return STTResult(transcript=decoded, language="hi-IN", confidence=0.95, is_final=True)
        except Exception:
            pass
            
        # Pick sample query deterministically based on hash of audio bytes
        query_idx = sum(audio_bytes[:20]) % len(self.sample_queries)
        transcript, lang = self.sample_queries[query_idx]
        
        return STTResult(
            transcript=transcript,
            language=lang,
            confidence=0.92,
            is_final=True
        )
