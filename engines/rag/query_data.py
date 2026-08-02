import logging
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from core.models import DomainType

logger = logging.getLogger("intent_rag_manager")

CHROMA_PATH = "chroma"

# Updated safety preamble – softer fallback, still anchored to context
SAFETY_PREAMBLE = """
You are VDA, a public-health information assistant.

NON-NEGOTIABLE RULES:
1. Use ONLY the retrieved context provided below. Do not use prior knowledge or model memory.
2. If the answer is not clearly supported by the retrieved context, say: "Based on the available guidance, I can only tell you that [insert relevant details from context]. For a complete answer, please consult a healthcare worker."
3. Do NOT diagnose diseases.
4. Do NOT prescribe medicines, change doses, or interpret lab results.
5. Do NOT generate free-form clinical advice.
6. Do NOT answer questions outside the approved use case for this prompt.
7. Do NOT mention or retain personal identifiers.
8. Never override a deterministic emergency escalation or clinician referral.
9. Keep the response short, factual, and easy to understand.
"""

ADHERENCE_PROMPT = SAFETY_PREAMBLE + """
Approved use case: UC1 NCD care adherence.
You may answer ONLY about:
- medication schedules already described in the context,
- follow-up timing already described in the context,
- annual screening reminders already described in the context,
- government-protocol self-care guidance explicitly present in the context.

Retrieved context:
{context}

Patient question:
{question}

Respond in 2-5 short sentences. Quote the schedule exactly if available.
"""

SCHEME_PROMPT = SAFETY_PREAMBLE + """
Approved use case: UC2 Scheme entitlement check.
You may answer ONLY about:
- eligibility criteria explicitly stated in the context,
- enrollment steps explicitly stated in the context,
- documents required explicitly stated in the context,
- benefits or coverage explicitly stated in the context.

Retrieved context:
{context}

Patient question:
{question}

Respond with a short checklist or numbered steps when possible.
"""

FACILITY_PROMPT = SAFETY_PREAMBLE + """
Approved use case: UC3 Public health service linkage.
You may answer ONLY about public facilities and services mentioned in the retrieved context.
When responding:
- name the facility if present in the context,
- mention the service available there,
- mention location or distance only if present in the context.

Retrieved context:
{context}

Patient question:
{question}

Respond in bullet points.
"""

TRIAGE_PROMPT = SAFETY_PREAMBLE + """
Approved use case: UC4 Teleconsultation & triage.
You may answer ONLY about:
- connecting to the teleconsultation service described in the context,
- referral instructions explicitly stated in the context,
- emergency escalation instructions explicitly stated in the context.

Retrieved context:
{context}

Patient question:
{question}

Respond in 1-3 short sentences.
"""

INTENT_PROMPTS = {
    DomainType.ADHERENCE: ADHERENCE_PROMPT,
    DomainType.SCHEMES: SCHEME_PROMPT,
    DomainType.FACILITY_LINKAGE: FACILITY_PROMPT,
    DomainType.TRIAGE: TRIAGE_PROMPT,
}

FALLBACK_RESPONSES = {
    "hi-IN": "Is vishay par abhi mere paas sarkari nirdesh ki jankari nahi hai. Kripya apne pas ke PHC center se sampark karein.",
    "en-IN": "I do not have official government protocol information for this query. Please contact your nearest PHC."
}

def build_search_query(domain: DomainType, query_text: str) -> str:
    if domain == DomainType.ADHERENCE:
        return f"medication schedule follow-up reminder screening {query_text}"
    elif domain == DomainType.SCHEMES:
        return f"eligibility enrollment PM-JAY Ayushman benefits coverage {query_text}"
    elif domain == DomainType.FACILITY_LINKAGE:
        return f"government hospital PHC district hospital public facility {query_text}"
    elif domain == DomainType.TRIAGE:
        return f"teleconsultation referral emergency escalation {query_text}"
    return query_text


class IntentRAGManager:
    def __init__(self, chroma_path: str = CHROMA_PATH):
        # Explicit embedding function
        self.embedding_function = OllamaEmbeddings(model="nomic-embed-text")
        self.db = Chroma(
            persist_directory=chroma_path,
            embedding_function=self.embedding_function
        )
        self.llm = Ollama(
            model="qwen3:8b",
            temperature=0.0,
            top_p=0.1,
            repeat_penalty=1.1
        )

    def query(self, domain: DomainType, query_text: str, language: str = "hi-IN", n_results: int = 10) -> str:
        """
        Retrieves chunks and generates an intent‑specific answer.
        n_results can be tuned (default 10) for better coverage.
        """
        try:
            search_query = build_search_query(domain, query_text)
            results = self.db.similarity_search_with_score(search_query, k=n_results)
            chunks = [doc.page_content for doc, _ in results]

            if not chunks:
                return FALLBACK_RESPONSES.get(language, FALLBACK_RESPONSES["hi-IN"])

            prompt_template_str = INTENT_PROMPTS.get(domain)
            if not prompt_template_str:
                return " ".join(chunks)

            context_text = "\n\n---\n\n".join(chunks)
            prompt = ChatPromptTemplate.from_template(prompt_template_str).format(
                context=context_text, question=query_text
            )
            response = self.llm.invoke(prompt)
            return response
        except Exception as e:
            logger.error(f"RAG error: {e}")
            return FALLBACK_RESPONSES.get(language, FALLBACK_RESPONSES["hi-IN"])