import logging
from config import settings
from core.models import DomainType, IntentResult
from engines.intent.rules import DOMAIN_KEYWORDS, OUT_OF_SCOPE_KEYWORDS

logger = logging.getLogger("intent_classifier")

class DeterministicIntentClassifier:
    """Deterministic Intent Router isolating queries to 4 core domains or rejecting out-of-scope queries."""

    def __init__(self):
        self.min_similarity = settings.INTENT_MIN_SIMILARITY

    def classify_intent(self, transcript: str) -> IntentResult:
        text_lower = transcript.lower()

        # 1. Check for Out-of-Scope triggers immediately
        for oos_kw in OUT_OF_SCOPE_KEYWORDS:
            if oos_kw in text_lower:
                logger.info(f"Out of scope keyword detected: '{oos_kw}'")
                return IntentResult(
                    domain=DomainType.OUT_OF_SCOPE,
                    confidence=1.0,
                    matched_keyword=oos_kw,
                    is_fallback=True
                )

        # 2. Rule-based Multi-lingual Keyword Matching across 4 domains
        domain_scores = {domain: 0 for domain in settings.APPROVED_DOMAINS}
        matched_keywords = {}

        for domain, keywords in DOMAIN_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    domain_scores[domain] += 1
                    if domain not in matched_keywords:
                        matched_keywords[domain] = kw

        # Get highest scoring domain
        best_domain = max(domain_scores, key=domain_scores.get)
        best_score = domain_scores[best_domain]

        if best_score > 0:
            logger.info(f"Deterministic keyword match: {best_domain} (Score: {best_score}, KW: {matched_keywords.get(best_domain)})")
            return IntentResult(
                domain=DomainType(best_domain),
                confidence=min(0.85 + (best_score * 0.05), 1.0),
                matched_keyword=matched_keywords.get(best_domain),
                is_fallback=False
            )

        # 3. If no keywords match, apply strict rejection fallback (do NOT guess intent)
        logger.info(f"No high-confidence domain match found for transcript: '{transcript}'. Falling back to OUT_OF_SCOPE.")
        return IntentResult(
            domain=DomainType.OUT_OF_SCOPE,
            confidence=0.0,
            is_fallback=True
        )
