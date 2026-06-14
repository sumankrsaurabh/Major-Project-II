import numpy as np
import logging
from typing import List

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available, using fallback embeddings")

class SemanticEmbeddings:
    """
    Semantic embedding model using sentence-transformers.
    Provides real semantic vector representations for better retrieval.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.vector_size = self.model.get_sentence_embedding_dimension()
        logger.info(f"✓ Loaded semantic embedding model: {model_name} ({self.vector_size}D)")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents using semantic model."""
        # Batch encode for efficiency
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return [emb.tolist() for emb in embeddings]

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query string using semantic model."""
        if not text:
            return np.zeros(self.vector_size).tolist()
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

class FallbackEmbeddings:
    """
    Fallback embedding model using TF-IDF-like hashing.
    Used when sentence-transformers is not available.
    """
    def __init__(self, vector_size: int = 384):
        self.vector_size = vector_size

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents into vectors."""
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query string into a vector."""
        if not text:
            return np.zeros(self.vector_size).tolist()
        
        # Improved hash-based embedding
        np.random.seed(hash(text) % (2**32))
        vector = np.random.randn(self.vector_size) * 0.1  # Smaller variance
        
        # Add character-level frequency information
        char_counts = {}
        for char in text.lower():
            if char.isalnum():
                char_counts[char] = char_counts.get(char, 0) + 1
        
        # Modify vector based on character frequencies
        for i, char in enumerate(sorted(char_counts.keys())[:min(50, self.vector_size)]):
            freq = char_counts[char] / len(text)
            vector[i] += freq * 2
        
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector.tolist()

_model = None

def get_embedding_model():
    """Get or create embedding model instance."""
    global _model
    if not _model:
        try:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                _model = SemanticEmbeddings(model_name="all-MiniLM-L6-v2")
                logger.info("✅ Using semantic embeddings (sentence-transformers)")
            else:
                _model = FallbackEmbeddings(vector_size=384)
                logger.warning("⚠️  Using fallback embeddings")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}, using fallback")
            _model = FallbackEmbeddings(vector_size=384)
    return _model