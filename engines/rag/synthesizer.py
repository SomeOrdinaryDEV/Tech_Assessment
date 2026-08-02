import logging
from core.models import DomainType, RAGContext

logger = logging.getLogger("rag_synthesizer")

class GroundedSynthesizer:
    """Grounded Response Synthesizer with intent-aware LLM generation."""

    def __init__(self, rag_manager=None):
        self.rag_manager = rag_manager  # IntentRAGManager instance
        self.fallback_responses = {
            "hi-IN": "Is vishay par abhi mere paas sarkari nirdesh ki jankari nahi hai. Kripya apne pas ke PHC center se sampark karein.",
            "ta-IN": "Indha thagaval patriya arikkai ennidamar illai. Kittiyirukkum PHC-ai thodarbu kollavum.",
            "te-IN": "Ee vishayampai naa daggara samacharam ledhu. Daggaralo unna PHC ni sampradhinchandi.",
            "ml-IN": "Ee vishayathekkurichulla vivaram illai. Aduthulla PHC-yumaay bandhappaduka.",
            "kn-IN": "Ee vishayadha bagge mahithi illa. Samipadha PHC ge bheti kodi.",
            "en-IN": "I do not have official government protocol information for this query. Please contact your nearest PHC."
        }

    def synthesize_response(
        self, 
        context: RAGContext, 
        query_text: str,
        language: str = "hi-IN"
    ) -> str:
        """
        Intent-aware synthesis:
        1. If no context, return language-specific fallback
        2. If context exists, use intent-specific LLM generation
        3. If no LLM available, join chunks directly
        """
        if not context.has_context or not context.retrieved_chunks:
            logger.warning(f"No grounded context for domain '{context.domain.value}'. Returning fallback.")
            return self.fallback_responses.get(language, self.fallback_responses["hi-IN"])

        # Use intent-aware LLM generation if available
        if self.rag_manager:
            try:
                response = self.rag_manager.generate_response(
                    domain=context.domain,
                    query_text=query_text,
                    context_chunks=context.retrieved_chunks
                )
                logger.info(f"Generated intent-specific response for {context.domain.value}")
                return response
            except Exception as e:
                logger.error(f"LLM generation failed: {e}. Falling back to chunk join.")
        
        # Fallback: join chunks directly
        synthesized_text = " ".join(context.retrieved_chunks)
        logger.info(f"Synthesized response from {len(context.retrieved_chunks)} chunks (no LLM)")
        return synthesized_text