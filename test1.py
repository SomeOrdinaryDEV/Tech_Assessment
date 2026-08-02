# test1.py
from engines.rag.query_data import IntentRAGManager
from core.models import DomainType

def main():
    rag = IntentRAGManager()

    # Predefined test cases – change or add your own
    tests = [
        (DomainType.ADHERENCE, "When should I take my TB medicine?", "en-IN"),
        (DomainType.SCHEMES, "Am I eligible for Ayushman Bharat?", "hi-IN"),
        (DomainType.FACILITY_LINKAGE, "Where is the nearest government hospital?", "en-IN"),
        (DomainType.TRIAGE, "I have chest pain, what should I do?", "en-IN"),
    ]

    print("=== Running predefined tests ===")
    for domain, query, lang in tests:
        print(f"\n>> Domain: {domain.value} | Query: {query}")
        response = rag.query(domain=domain, query_text=query, language=lang, n_results=10)
        print(f">> Response: {response}")

    print("\n=== Interactive mode (type 'quit' to exit) ===")
    while True:
        q = input("\nQuery: ").strip()
        if q.lower() == "quit":
            break
        d = input("Domain (adherence/schemes/facility_linkage/triage): ").strip().lower()
        lang = input("Language (hi-IN/en-IN, default hi-IN): ").strip() or "hi-IN"

        domain_map = {
            "adherence": DomainType.ADHERENCE,
            "schemes": DomainType.SCHEMES,
            "facility_linkage": DomainType.FACILITY_LINKAGE,
            "triage": DomainType.TRIAGE,
        }
        domain = domain_map.get(d)
        if not domain:
            print("Invalid domain, using TRIAGE as default.")
            domain = DomainType.TRIAGE

        response = rag.query(domain=domain, query_text=q, language=lang, n_results=10)
        print(f"Response: {response}")

if __name__ == "__main__":
    main()