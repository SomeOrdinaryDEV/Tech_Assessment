from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class DomainType(str, Enum):
    ADHERENCE = "adherence"
    SCHEMES = "schemes"
    FACILITY_LINKAGE = "facility_linkage"
    TRIAGE = "triage"
    OUT_OF_SCOPE = "out_of_scope"
    LOW_CONFIDENCE = "low_confidence"

class STTResult(BaseModel):
    transcript: str
    translation: str
    language: str = "hi-IN"
    confidence: float = 1.0
    is_final: bool = True

class IntentResult(BaseModel):
    domain: DomainType
    confidence: float
    matched_keyword: Optional[str] = None
    is_fallback: bool = False

class SafetyResult(BaseModel):
    is_emergency: bool = False
    red_flag_rule: Optional[str] = None
    matched_keyword: Optional[str] = None
    override_message: Optional[Dict[str, str]] = None  # Localized emergency message map
    requires_escalation: bool = False

class PipelineResponse(BaseModel):
    session_id: str
    transcript: str
    translation: str
    language: str
    domain: DomainType
    text_response: str
    audio_b64: Optional[str] = None
    is_emergency: bool = False
    is_rejection: bool = False
    escalation_triggered: bool = False

class EscalationPayload(BaseModel):
    patient_id: str
    session_id: str
    language: str
    transcript: str
    red_flag_rule: str
    matched_keyword: str
    timestamp: str
    status: str = "PENDING_DOCTOR_JOIN"

class RAGContext(BaseModel):
    """RAG context with domain tracking for intent-aware processing."""
    domain: DomainType  # Keep domain for tracking
    retrieved_chunks: List[str] = Field(default_factory=list)
    source_documents: List[str] = Field(default_factory=list)
    has_context: bool = False
