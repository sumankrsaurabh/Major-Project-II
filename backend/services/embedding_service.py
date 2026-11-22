import logging
import os
from typing import List

import numpy as np

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
except ImportError as exc:
    SentenceTransformer = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


class SemanticEmbeddings:
    """Local sentence-transformer embeddings used for semantic retrieval."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        if SentenceTransformer is None:
            raise RuntimeError(
                "sentence-transformers is required for semantic retrieval; "
                "install backend requirements before starting the API"
            ) from _IMPORT_ERROR

        self.model_name = model_name
        cache_dir = os.getenv("SENTENCE_TRANSFORMERS_HOME")
        local_only = os.getenv("LOCAL_MODELS_ONLY", "true").lower() in {"1", "true", "yes"}
        try:
            self.model = SentenceTransformer(
                model_name,
                cache_folder=cache_dir,
                local_files_only=local_only,
            )
        except TypeError:
            # Older sentence-transformers versions may not expose local_files_only.
            if local_only:
                raise RuntimeError(
                    "Installed sentence-transformers does not support strict local-only loading. "
                    "Upgrade it or set LOCAL_MODELS_ONLY=false explicitly."
                )
            self.model = SentenceTransformer(model_name, cache_folder=cache_dir)

        self.vector_size = self.model.get_sentence_embedding_dimension()
        if not self.vector_size:
            raise RuntimeError("Embedding model returned an invalid vector dimension")
        logger.info("Loaded local embedding model %s (%s dimensions)", model_name, self.vector_size)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        vectors = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(vectors, dtype=np.float32).tolist()

    def embed_query(self, text: str) -> List[float]:
        if not text.strip():
            return np.zeros(self.vector_size, dtype=np.float32).tolist()
        vector = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(vector, dtype=np.float32).tolist()


_model = None


def get_embedding_model():
    """Return the process-wide embedding model; never silently fake semantic vectors."""
    global _model
    if _model is None:
        model_name = os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        )
        _model = SemanticEmbeddings(model_name=model_name)
    return _model
