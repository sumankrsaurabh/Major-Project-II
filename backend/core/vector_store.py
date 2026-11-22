import json
import os
import re
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

import numpy as np

from config import VECTOR_PATH
from services.embedding_service import get_embedding_model


WORKSPACE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
DOCUMENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

_store_lock = threading.RLock()


@contextmanager
def _workspace_write_transaction(workspace_id: str):
    """Serialize index mutations across processes with a SQLite write transaction.

    The lock database lives beside the indexes, so deleting the last document
    cannot remove the lock protecting that workspace.
    """
    base = Path(VECTOR_PATH).resolve()
    base.mkdir(parents=True, exist_ok=True)
    lock_db = base / ".workspace-locks.sqlite3"
    connection = sqlite3.connect(str(lock_db), timeout=30, isolation_level=None)
    try:
        connection.execute("PRAGMA busy_timeout = 30000")
        connection.execute(
            "CREATE TABLE IF NOT EXISTS workspace_locks ("
            "workspace_id TEXT PRIMARY KEY, touched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "INSERT INTO workspace_locks(workspace_id) VALUES (?) "
            "ON CONFLICT(workspace_id) DO UPDATE SET touched_at=CURRENT_TIMESTAMP",
            (validate_workspace_id(workspace_id),),
        )
        yield
        connection.execute("COMMIT")
    except Exception:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise
    finally:
        connection.close()


def validate_workspace_id(workspace_id: str) -> str:
    if not isinstance(workspace_id, str) or not WORKSPACE_ID_PATTERN.fullmatch(workspace_id):
        raise ValueError("Invalid workspace identifier")
    return workspace_id


def validate_document_id(document_id: str) -> str:
    if not isinstance(document_id, str) or not DOCUMENT_ID_PATTERN.fullmatch(document_id):
        raise ValueError("Invalid document identifier")
    return document_id


def _workspace_path(workspace_id: str) -> Path:
    workspace_id = validate_workspace_id(workspace_id)
    base = Path(VECTOR_PATH).resolve()
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
    """Workspace-scoped NumPy index persisted as one atomic archive."""

    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.documents = []
        self.vectors = None
        self._lock = threading.RLock()

    def add_documents(self, documents: list[NativeDocument]):
        if not documents:
            return
        embeddings = self.embedding_model.embed_documents([doc.page_content for doc in documents])
        new_vectors = np.asarray(embeddings, dtype=np.float32)
        if new_vectors.ndim != 2 or len(new_vectors) != len(documents):
            raise ValueError("Embedding provider returned an invalid document matrix")
        with self._lock:
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
        return [
            NativeDocument(
                self.documents[int(index)].page_content,
                {**self.documents[int(index)].metadata, "score": float(similarities[index])},
            )
            for index in top_indices
        ]

    def remove_document(self, document_id: str) -> bool:
        with self._lock:
            keep = [
                index for index, doc in enumerate(self.documents)
                if doc.metadata.get("document_id", "legacy") != document_id
            ]
            if len(keep) == len(self.documents):
                return False
            self.documents = [self.documents[index] for index in keep]
            self.vectors = self.vectors[keep] if keep else None
            return True

    def save_local(self, folder_path: str):
        with self._lock:
            path = Path(folder_path)
            path.mkdir(parents=True, exist_ok=True)
            archive = path / "index.npz"
            temporary = path / f".index-{os.getpid()}-{threading.get_ident()}.tmp"
            docs_json = json.dumps(
                [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in self.documents],
                ensure_ascii=False,
            )
        # A single archive means vectors and their document metadata are swapped together.
            with temporary.open("wb") as output:
                np.savez_compressed(
                    output,
                    vectors=self.vectors if self.vectors is not None else np.empty((0, 0), dtype=np.float32),
                    documents=np.asarray(docs_json),
                    format_version=np.asarray(1, dtype=np.int64),
                )
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, archive)

    @classmethod
    def load_local(cls, folder_path: str, embedding_model):
        path = Path(folder_path)
        archive = path / "index.npz"
        if archive.is_file():
            with np.load(archive, allow_pickle=False) as data:
                vectors = data["vectors"]
                docs_data = json.loads(str(data["documents"].item()))
            store = cls(embedding_model)
            store.vectors = vectors if vectors.size else None
            store.documents = [
                NativeDocument(item["page_content"], item.get("metadata", {}))
                for item in docs_data
            ]
        else:
            # Read the earlier two-file format for a non-disruptive upgrade.
            vec_file, doc_file = path / "vectors.npy", path / "documents.json"
            if not vec_file.is_file() or not doc_file.is_file():
                return None
            store = cls(embedding_model)
            store.vectors = np.load(vec_file, allow_pickle=False)
            with doc_file.open("r", encoding="utf-8") as source:
                docs_data = json.load(source)
            store.documents = [
                NativeDocument(item["page_content"], item.get("metadata", {}))
                for item in docs_data
            ]
        if store.vectors is None or store.vectors.ndim != 2 or store.vectors.shape[0] != len(store.documents):
            raise ValueError("Workspace vector index is corrupt or inconsistent")
        return store


def create_vector_store(
    chunks: list[str],
    workspace_id: str = "default",
    document_id: str = "legacy",
    filename: str = "Imported document",
    chunk_metadata: list[dict] | None = None,
):
    """Append a document's chunks to the selected workspace index."""
    path = _workspace_path(workspace_id)
    document_id = validate_document_id(document_id)
    with _store_lock, _workspace_write_transaction(workspace_id):
        # Reload under the cross-process lock. A process-local cache could
        # otherwise overwrite changes committed by another worker.
        store = CustomVectorStore.load_local(str(path), get_embedding_model())
        if store is None:
            store = CustomVectorStore(get_embedding_model())
        if chunk_metadata is not None and len(chunk_metadata) != len(chunks):
            raise ValueError("Chunk metadata count must match the chunk count")
        documents = [
            NativeDocument(
                page_content=chunk,
                metadata={
                    "document_id": document_id,
                    "filename": filename,
                    "chunk_index": index,
                    **(chunk_metadata[index] if chunk_metadata is not None else {}),
                },
            )
            for index, chunk in enumerate(chunks) if chunk.strip()
        ]
        store.add_documents(documents)
        store.save_local(str(path))
        return store


def list_workspace_documents(workspace_id: str = "default"):
    store = load_vector_store(workspace_id)
    if store is None:
        return []
    documents = {}
    for chunk in store.documents:
        doc_id = chunk.metadata.get("document_id", "legacy")
        record = documents.setdefault(doc_id, {
            "document_id": doc_id,
            "filename": chunk.metadata.get("filename", "Imported document"),
            "chunks": 0,
        })
        record["chunks"] += 1
    return list(documents.values())


def delete_workspace_document(workspace_id: str, document_id: str):
    """Remove a document and its vectors from one workspace."""
    path = _workspace_path(workspace_id)
    document_id = validate_document_id(document_id)
    with _store_lock, _workspace_write_transaction(workspace_id):
        # Reload inside the transaction so deletes preserve concurrent additions.
        store = CustomVectorStore.load_local(str(path), get_embedding_model())
        if store is None:
            return False
        if not store.remove_document(document_id):
            return False
        if store.documents:
            store.save_local(str(path))
        else:
            (path / "index.npz").unlink(missing_ok=True)
            # Remove legacy files only after the workspace has no indexed content.
            (path / "vectors.npy").unlink(missing_ok=True)
            (path / "documents.json").unlink(missing_ok=True)
        return True


def load_vector_store(workspace_id: str = "default"):
    """Load only the selected workspace index; never fall back to another workspace."""
    path = _workspace_path(workspace_id)
    # Never serve a long-lived process-local snapshot: another worker may
    # have committed a newer index since this process last loaded it.
    with _store_lock:
        return CustomVectorStore.load_local(str(path), get_embedding_model())


def clear_vector_store_cache():
    """Compatibility no-op; indexes are intentionally never cached in process."""
    return None
