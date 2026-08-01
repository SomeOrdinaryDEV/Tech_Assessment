import logging
from core.models import RAGContext

logger = logging.getLogger("rag_synthesizer")

class GroundedSynthesizer:
    """Grounded Response Synthesizer strictly bounded by retrieved context chunks."""

    def __init__(self):
        self.fallback_responses = {
            "hi-IN": "Is vishay par abhi mere paas sarkari nirdesh ki jankari nahi hai. Kripya apne pas ke PHC center se sampark karein.",
            "ta-IN": "Indha thagaval patriya arikkai ennidamar illai. Kittiyirukkum PHC-ai thodarbu kollavum.",
            "te-IN": "Ee vishayampai naa daggara samacharam ledhu. Daggaralo unna PHC ni sampradhinchandi.",
            "ml-IN": "Ee vishayathekkurichulla vivaram illai. Aduthulla PHC-yumaay bandhappaduka.",
            "kn-IN": "Ee vishayadha bagge mahithi illa. Samipadha PHC ge bheti kodi.",
            "en-IN": "I do not have official government protocol information for this query. Please contact your nearest PHC."
        }

    def synthesize_response(self, context: RAGContext, language: str = "hi-IN") -> str:
        if not context.has_context or not context.retrieved_chunks:
            logger.warning(f"No grounded context retrieved for domain '{context.domain.value}'. Returning strict fallback.")
            return self.fallback_responses.get(language, self.fallback_responses["hi-IN"])

        # Grounded context synthesis (joining clean retrieved chunks)
        synthesized_text = " ".join(context.retrieved_chunks)
        logger.info(f"Synthesized response strictly from {len(context.retrieved_chunks)} context chunks.")
        return synthesized_text
