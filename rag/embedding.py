from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()


class EmbeddingModel:
    def __init__(self):
        # Use SentenceTransformers for mean pooling (optimized for similarity search)
        self.model_name = "BAAI/bge-large-en-v1.5"
        self.model = SentenceTransformer(self.model_name)

    def embed_text(self, text: str):
        """Generates an embedding for the given text using mean pooling"""
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,  # normalize for cosine similarity
        )
        return embedding.tolist()


# Singleton instance
embedding_model = EmbeddingModel()
