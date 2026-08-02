import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Medtronics_Project"
    BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
    
    # Target Languages & Speech Settings
    SUPPORTED_LANGUAGES: list[str] = [
        "hi-IN",  # Hindi
        "ta-IN",  # Tamil
        "te-IN",  # Telugu
        "ml-IN",  # Malayalam
        "kn-IN",  # Kannada
        "en-IN",  # Hinglish / English
    ]
    DEFAULT_LANGUAGE: str = "hi-IN"
    
    # Confidence & Safety Thresholds
    STT_MIN_CONFIDENCE: float = 0.85
    INTENT_MIN_SIMILARITY: float = 0.85
    
    # Approved 4 Core Domains
    APPROVED_DOMAINS: list[str] = ["adherence", "schemes", "facility_linkage", "triage"]
    
    # Vector DB Settings
    CHROMA_PERSIST_DIR: str = os.path.join(BASE_DIR, "data", "chroma_db")
    
    # STT Engine Selection: 'sarvam', 'google', or 'mock'
    STT_ENGINE_TYPE: str = os.getenv("STT_ENGINE_TYPE", "sarvam").lower()
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    
    # Google Cloud Settings
    USE_GOOGLE_CLOUD: bool = os.getenv("USE_GOOGLE_CLOUD", "true").lower() == "true"
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

settings = Settings()
