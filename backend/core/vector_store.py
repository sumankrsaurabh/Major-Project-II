import json
import os
import re
import threading
from pathlib import Path

import numpy as np

from config import VECTOR_PATH
from services.embedding_service import get_embedding_model


WORKSPACE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
_store_cache = {}
_store_lock = threading.RLock()


def validate_workspace_id(workspace_id: str) -> str:
    """Validate an opaque workspace key before using it in a storage path."""
    if not isinstance(workspace_id, str) or not WORKSPACE_ID_PATTERN.fullmatch(workspace_id):
        raise ValueError("Invalid workspace identifier")
    return workspace_id


def _workspace_path(workspace_id: str) -> Path:
    workspace_id = validate_workspace_id(workspace_id)
    base = Path(VECTOR_PATH).resolve()
    # Preserve the historical index location for the compatibility workspace.
    target = base if workspace_id == "default" else base / "workspaces" / workspace_id
    resolved = target.resolve()
    if resolved != base and base not in resolved.parents:
        raise ValueError("Workspace storage path is outside the configured index directory")
    return resolved


class NativeDocument:
    """A document passage and its source metadata."""

    def __init__(self, page_content: str, metadata: dict = None):
        self.page_content = page_content
        self.metadata = metadata or {}


class CustomVectorStore:
    """NumPy cosine-similarity index scoped to a single workspace."""

    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.documents = []
        self.vectors = None

    def add_documents(self, documents: list[NativeDocument]):
        if not documents:
            return
        embeddings = self.embedding_model.embed_documents([doc.page_content for doc in documents])
        new_vectors = np.asarray(embeddings, dtype=np.float32)
        if new_vectors.ndim != 2 or len(new_vectors) != len(documents):
            raise ValueError("Embedding provider returned an invalid document matrix")
        if self.vectors is None:
            self.vectors = new_vectors
        else:
            if self.vectors.shape[1] != new_vectors.shape[1]:
                raise ValueError("Embedding dimensions do not match the existing workspace index")
            self.vectors = np.vstack([self.vectors, new_vectors])
        self.documents.extend(documents)

    def similarity_search(self, query: str, k: int = 4) -> list[NativeDocument]:
        if self.vectors is None or not self.documents or k <= 0:
            return []
        query_vector = np.asarray(self.embedding_model.embed_query(query), dtype=np.float32)
        if query_vector.ndim != 1 or query_vector.shape[0] != self.vectors.shape[1]:
            raise ValueError("Query embedding dimensions do not match the workspace index")
        similarities = np.dot(self.vectors, query_vector)
        top_indices = np.argsort(similarities)[::-1][:k]
        results = []
        for index in top_indices:
            doc = self.documents[int(index)]
            # Copy metadata so concurrent searches cannot overwrite each other's score.
            metadata = dict(doc.metadata)
            metadata["score"] = float(similarities[index])
            results.append(NativeDocument(doc.page_content, metadata))
        return results

    def save_local(self, folder_path: str):
        path = Path(folder_path)
        path.mkdir(parents=True, exist_ok=True)
        docs_data = [
            {"page_content": doc.page_content, "metadata": doc.metadata}
            for doc in self.documents
        ]
        vectors_tmp = path / "vectors.tmp.npy"
        docs_tmp = path / "documents.tmp.json"
        if self.vectors is not None:
            np.save(vectors_tmp, self.vectors)
        with docs_tmp.open("w", encoding="utf-8") as output:
            json.dump(docs_data, output, ensure_ascii=False)
        if self.vectors is not None:
            os.replace(vectors_tmp, path / "vectors.npy")
        os.replace(docs_tmp, path / "documents.json")

    @classmethod
    def load_local(cls, folder_path: str, embedding_model):
        path = Path(folder_path)
        vec_file = path / "vectors.npy"
        doc_file = path / "documents.json"
        if not vec_file.is_file() or not doc_file.is_file():
            return None
        store = cls(embedding_model)
        store.vectors = np.load(vec_file, allow_pickle=False)
        with doc_file.open("r", encoding="utf-8") as source:
            docs_data = json.load(source)
        store.documents = [
            NativeDocument(page_content=item["page_content"], metadata=item.get("metadata", {}))
            for item in docs_data
        ]
        if store.vectors.ndim != 2 or store.vectors.shape[0] != len(store.documents):
            raise ValueError("Workspace vector index is corrupt or inconsistent")
        return store


def create_vector_store(chunks: list[str], workspace_id: str = "default"):
    """Create or append chunks to the selected workspace index."""
    path = _workspace_path(workspace_id)
    with _store_lock:
        store = _store_cache.get(workspace_id)
        if store is None:
            store = CustomVectorStore.load_local(str(path), get_embedding_model())
        if store is None:
            store = CustomVectorStore(get_embedding_model())
        documents = [NativeDocument(page_content=chunk) for chunk in chunks if chunk.strip()]
        store.add_documents(documents)
        store.save_local(str(path))
        _store_cache[workspace_id] = store
        return store


def load_vector_store(workspace_id: str = "default"):
    """Load only the selected workspace index; never fall back to another workspace."""
    path = _workspace_path(workspace_id)
    with _store_lock:
        if workspace_id in _store_cache:
            return _store_cache[workspace_id]
        store = CustomVectorStore.load_local(str(path), get_embedding_model())
        if store is not None:
            _store_cache[workspace_id] = store
        return store


def clear_vector_store_cache():
    """Clear in-memory indexes; primarily useful for tests and controlled reloads."""
    with _store_lock:
        _store_cache.clear()
