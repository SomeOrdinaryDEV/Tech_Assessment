import os
import json
import logging
import chromadb
from config import settings
from core.models import DomainType, RAGContext

logger = logging.getLogger("rag_partition_manager")

class PartitionedRAGManager:
    """Manager for 4 physically isolated ChromaDB collections to prevent cross-contamination."""

    def __init__(self):
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collections = {}
        self._init_collections()

    def _init_collections(self):
        """Creates physically separate collections for the 4 core domains."""
        for domain in settings.APPROVED_DOMAINS:
            coll_name = f"{domain}_col"
            collection = self.client.get_or_create_collection(name=coll_name)
            self.collections[domain] = collection
            self._seed_data_if_empty(domain, collection)

    def _seed_data_if_empty(self, domain: str, collection):
        """Seeds domain knowledge base documents if collection is empty."""
        if collection.count() == 0:
            json_file = os.path.join(settings.BASE_DIR, "data", domain, f"{domain}_db.json")
            if not os.path.exists(json_file):
                # Check alternative names
                file_map = {
                    "adherence": "tb_nikshay_guidelines.json",
                    "schemes": "ayushman_bharat_pmjay.json",
                    "facility_linkage": "phc_chc_directory.json",
                    "triage": "clinical_triage_rules.json"
                }
                json_file = os.path.join(settings.BASE_DIR, "data", domain, file_map.get(domain, ""))

            if os.path.exists(json_file):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    ids, docs, metadatas = [], [], []
                    for item in data:
                        ids.append(item["id"])
                        docs.append(item["content"])
                        metadatas.append({"topic": item.get("topic", ""), "domain": domain})

                        # Add translations if present
                        translations = item.get("translations", {})
                        for lang, trans_text in translations.items():
                            ids.append(f"{item['id']}_{lang}")
                            docs.append(trans_text)
                            metadatas.append({"topic": item.get("topic", ""), "domain": domain, "lang": lang})

                    if docs:
                        collection.add(ids=ids, documents=docs, metadatas=metadatas)
                        logger.info(f"Seeded {len(docs)} documents into isolated collection: {domain}_col")
                except Exception as e:
                    logger.error(f"Error seeding domain '{domain}': {e}")

    def query_isolated_domain(self, domain: DomainType, query_text: str, n_results: int = 2) -> RAGContext:
        """Strictly queries ONLY the targeted domain's collection."""
        domain_str = domain.value
        if domain_str not in self.collections:
            logger.warning(f"Attempted RAG query on invalid or out-of-scope domain: '{domain_str}'")
            return RAGContext(domain=domain, retrieved_chunks=[], source_documents=[], has_context=False)

        target_collection = self.collections[domain_str]
        try:
            results = target_collection.query(query_texts=[query_text], n_results=n_results)
            retrieved_chunks = results["documents"][0] if results and results.get("documents") else []
            sources = [m.get("topic", "") for m in results["metadatas"][0]] if results and results.get("metadatas") else []

            has_context = len(retrieved_chunks) > 0
            logger.info(f"RAG Retrieval from isolated collection '{domain_str}_col': Found {len(retrieved_chunks)} chunks.")
            
            return RAGContext(
                domain=domain,
                retrieved_chunks=retrieved_chunks,
                source_documents=sources,
                has_context=has_context
            )
        except Exception as e:
            logger.error(f"Error querying ChromaDB collection '{domain_str}_col': {e}")
            return RAGContext(domain=domain, retrieved_chunks=[], source_documents=[], has_context=False)
