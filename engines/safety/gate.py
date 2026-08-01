import logging
from core.models import SafetyResult
from engines.safety.red_flags import RED_FLAG_RULES, EMERGENCY_OVERRIDE_MESSAGES

logger = logging.getLogger("safety_gate")

class DeterministicSafetyGate:
    """Non-ML Hardcoded Rule Engine for evaluating clinical emergencies."""

    def evaluate_safety(self, transcript: str, generated_text: str = "") -> SafetyResult:
        combined_text = f"{transcript} {generated_text}".lower()

        for rule_name, keywords in RED_FLAG_RULES.items():
            for kw in keywords:
                if kw in combined_text:
                    logger.warning(f"CRITICAL SAFETY RED FLAG TRIGGERED: Rule='{rule_name}', Keyword='{kw}'")
                    return SafetyResult(
                        is_emergency=True,
                        red_flag_rule=rule_name,
                        matched_keyword=kw,
                        override_message=EMERGENCY_OVERRIDE_MESSAGES,
                        requires_escalation=True
                    )

        return SafetyResult(is_emergency=False, requires_escalation=False)
