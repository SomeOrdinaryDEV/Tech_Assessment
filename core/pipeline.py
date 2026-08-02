import time
import logging
import uuid
from config import settings
from core.models import DomainType, PipelineResponse, EscalationPayload
from engines.stt.google_stt import GoogleSTTEngine
from engines.intent.classifier import DeterministicIntentClassifier
from engines.rag.partition_manager import PartitionedRAGManager
from engines.rag.synthesizer import GroundedSynthesizer
from engines.safety.gate import DeterministicSafetyGate
from engines.safety.telemetry import telemetry_tracker
from engines.tts.google_tts import GoogleTTSEngine
from engines.translator.sarvam_translator import SarvamTranslatorEngine
from portal.teleconsult import teleconsult_portal

logger = logging.getLogger("core_pipeline")

class MedtronicsCorePipeline:
    """Main Orchestration Pipeline uniting STT, Translator, Intent Router, RAG, Safety Gate, TTS, and Teleconsultation."""

    def __init__(self):
        # Select STT Engine based on config
        if settings.STT_ENGINE_TYPE == "sarvam":
            from engines.stt.sarvam_sttt import SarvamSTTEngine
            self.stt_engine = SarvamSTTEngine()
        elif settings.STT_ENGINE_TYPE == "google":
            from engines.stt.google_stt import GoogleSTTEngine
            self.stt_engine = GoogleSTTEngine()
        else:
            from engines.stt.mock_stt import MockSTTEngine
            self.stt_engine = MockSTTEngine()

        self.translator = SarvamTranslatorEngine()
        self.intent_classifier = DeterministicIntentClassifier()
        self.rag_manager = PartitionedRAGManager()
        self.synthesizer = GroundedSynthesizer()
        self.safety_gate = DeterministicSafetyGate()
        self.tts_engine = GoogleTTSEngine()

    async def process_voice_input(self, audio_bytes: bytes, session_id: str = None) -> PipelineResponse:
        start_time = time.time()
        session_id = session_id or str(uuid.uuid4())[:8]

        # Step 1: STT & Language Detection
        stt_result = await self.stt_engine.transcribe_audio_bytes(audio_bytes)
        logger.info(f"[{session_id}] STT Result: \nTranscript: '{stt_result.transcript}'\nTranslation: '{stt_result.translation}'\n  (Lang: {stt_result.language}, Conf: {stt_result.confidence})")

        # Step 2: Confidence Filter Gate (< 0.65 Re-Ask)
        if not stt_result.transcript or stt_result.confidence < settings.STT_MIN_CONFIDENCE:
            reask_text = "Aapki aawaz saaf nahi aayi, kripya dubara bolein."
            audio_b64 = await self.tts_engine.synthesize_speech(reask_text, stt_result.language)
            return PipelineResponse(
                session_id=session_id,
                transcript=stt_result.transcript,
                translation=stt_result.translation,
                language=stt_result.language,
                domain=DomainType.LOW_CONFIDENCE,
                text_response=reask_text,
                audio_b64=audio_b64,
                is_rejection=True
            )

        # Step 3: Safety Gate Dual-Pass (Evaluate raw transcript BEFORE RAG)
        safety_eval = self.safety_gate.evaluate_safety(stt_result.transcript)
        if safety_eval.is_emergency:
            return await self._handle_emergency_escalation(session_id, stt_result, safety_eval, start_time)

        # Step 4: Translate Native Indic Script to English Search Query (e.g. 'भारत' -> 'Bharat')
        search_query = await self.translator.translate_to_english(stt_result.transcript, stt_result.language)
        logger.info(f"[{session_id}] Translated Search Query for RAG: '{search_query}'")

        # Step 5: Deterministic Intent Router (Evaluates raw + translated text)
        intent_result = self.intent_classifier.classify_intent(f"{stt_result.transcript} {search_query}")
        logger.info(f"[{session_id}] Classified Domain: {intent_result.domain.value}")

        # Step 6: Handle Out-of-Scope / Rejection Node
        if intent_result.domain == DomainType.OUT_OF_SCOPE:
            rejection_text = "Main srif dawaiyan, sarkari yojana, aspatal, aur swasthya jaanch me madad kar sakta hoon."
            audio_b64 = await self.tts_engine.synthesize_speech(rejection_text, stt_result.language)
            return PipelineResponse(
                session_id=session_id,
                transcript=stt_result.transcript,
                translation=stt_result.translation,
                language=stt_result.language,
                domain=DomainType.OUT_OF_SCOPE,
                text_response=rejection_text,
                audio_b64=audio_b64,
                is_rejection=True
            )

        # Step 7: Isolated RAG Retrieval using Translated Query
        rag_context = self.rag_manager.query_isolated_domain(intent_result.domain, search_query)

        # Step 8: Grounded Response Synthesizer
        text_response = self.synthesizer.synthesize_response(rag_context, stt_result.language)

        # Step 9: Safety Gate Output Pass (Evaluate generated response)
        output_safety_eval = self.safety_gate.evaluate_safety(stt_result.transcript, text_response)
        if output_safety_eval.is_emergency:
            return await self._handle_emergency_escalation(session_id, stt_result, output_safety_eval, start_time)

        # Step 10: Low-Latency TTS Synthesis
        audio_b64 = await self.tts_engine.synthesize_speech(text_response, stt_result.language)

        latency_ms = (time.time() - start_time) * 1000
        telemetry_tracker.log_event(session_id, stt_result.transcript, False, "", latency_ms)

        return PipelineResponse(
            session_id=session_id,
            transcript=stt_result.transcript,
            translation=stt_result.translation,
            language=stt_result.language,
            domain=intent_result.domain,
            text_response=text_response,
            audio_b64=audio_b64,
            is_emergency=False,
            is_rejection=False
        )

    async def _handle_emergency_escalation(self, session_id: str, stt_result, safety_eval, start_time: float) -> PipelineResponse:
        emergency_text = safety_eval.override_message.get(stt_result.language, safety_eval.override_message["hi-IN"])
        audio_b64 = await self.tts_engine.synthesize_speech(emergency_text, stt_result.language)

        escalation_payload = EscalationPayload(
            patient_id=f"PATIENT-{session_id}",
            session_id=session_id,
            language=stt_result.language,
            transcript=stt_result.transcript,
            red_flag_rule=safety_eval.red_flag_rule,
            matched_keyword=safety_eval.matched_keyword,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )

        # Broadcast alert to Clinician Teleconsultation Portal
        await teleconsult_portal.broadcast_escalation(escalation_payload)

        latency_ms = (time.time() - start_time) * 1000
        telemetry_tracker.log_event(session_id, stt_result.transcript, True, safety_eval.red_flag_rule, latency_ms)

        return PipelineResponse(
            session_id=session_id,
            transcript=stt_result.transcript,
            translation=stt_result.translation,
            language=stt_result.language,
            domain=DomainType.TRIAGE,
            text_response=emergency_text,
            audio_b64=audio_b64,
            is_emergency=True,
            escalation_triggered=True
        )
