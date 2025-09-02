import os
import chromadb
from typing import List, Dict, Any, Optional
from .embedding import embedding_model
from dotenv import load_dotenv
from sentence_transformers import CrossEncoder
from joblib import Memory
from database.schemas import Patient

load_dotenv()

# Setup caching (stored under .cache/retriever/)
memory = Memory(location=".cache/retriever", verbose=0)


class ChromaRetriever:
    def __init__(self):
        db_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "database", "chroma_db")
        )
        self.client = chromadb.PersistentClient(path=db_path)
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    @memory.cache
    def query_collection(
        self,
        collection_name: str,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """Query a specific collection with optional filters, rerank results"""
        try:
            collection = self.client.get_collection(name=collection_name)
            query_embedding = embedding_model.embed_text(query)

            # Build where clause with richer operators
            where_clause = self._build_where(filters)

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results * 2,  # get more, then rerank
                where=where_clause,
            )

            if not results["documents"]:
                return []

            # Prepare candidates
            docs = [
                {
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
                for i in range(len(results["documents"][0]))
            ]

            # Apply reranking
            pairs = [(query, d["document"]) for d in docs]
            scores = self.reranker.predict(pairs)
            for i, score in enumerate(scores):
                docs[i]["rerank_score"] = float(score)

            # Sort by rerank_score
            docs = sorted(docs, key=lambda x: x["rerank_score"], reverse=True)

            return docs[:n_results]
        except Exception as e:
            print(f"Error querying collection {collection_name}: {e}")
            return []

    def get_patient_info(self, patient_id: str) -> Optional[Patient]:
        """Get specific patient information by ID, validated with schema"""
        try:
            collection = self.client.get_collection(name="patients")
            results = collection.get(where={"patient_id": {"$eq": patient_id}})

            if results["ids"]:
                raw_doc = results["documents"][0]
                # Validate & return Patient schema
                return Patient.parse_raw(raw_doc)
            else:
                return None
        except Exception as e:
            print(
                f"Error retrieving patient {patient_id}: {e}, "
                "This patient does not exist in the database. Please ask about an existing patient."
            )
            return None

    def get_collection_names(self) -> List[str]:
        """Get list of all available collections"""
        return [col.name for col in self.client.list_collections()]

    def _build_where(self, filters: Optional[Dict]) -> Optional[Dict]:
        """Build flexible where clause supporting $eq, $contains, $gte, $lte"""
        if not filters:
            return None
        where_clause = {"$and": []}
        for key, condition in filters.items():
            if isinstance(condition, dict):  # operator-based filter
                where_clause["$and"].append({key: condition})
            else:  # default to equality
                where_clause["$and"].append({key: {"$eq": condition}})
        return where_clause


# Singleton instance
chroma_retriever = ChromaRetriever()
