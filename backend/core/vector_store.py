import os
import numpy as np
import json
from pathlib import Path
from services.embedding_service import get_embedding_model
from config import VECTOR_PATH

class NativeDocument:
    """A simple document representation."""
    def __init__(self, page_content: str, metadata: dict = None):
        self.page_content = page_content
        self.metadata = metadata or {}

class CustomVectorStore:
    """
    A native tensor-based vector store using NumPy.
    Replaces FAISS for zero-dependency architecture.
    """
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.documents = []
        self.vectors = None

    def add_documents(self, documents: list[NativeDocument]):
        """Embed and add documents to the store."""
        texts = [doc.page_content for doc in documents]
        embeddings = self.embedding_model.embed_documents(texts)
        
        new_vectors = np.array(embeddings, dtype=np.float32)
        
        if self.vectors is None:
            self.vectors = new_vectors
        else:
            self.vectors = np.vstack([self.vectors, new_vectors])
            
        self.documents.extend(documents)

    def similarity_search(self, query: str, k: int = 4) -> list[NativeDocument]:
        """Search for top k most similar documents using cosine similarity."""
        if self.vectors is None or len(self.documents) == 0:
            return []

        query_vector = np.array(self.embedding_model.embed_query(query), dtype=np.float32)
        
        # Calculate cosine similarity
        # Assuming vectors are already normalized (from CustomEmbeddings)
        # If not normalized, you would do: query_vector / np.linalg.norm(query_vector)
        # and self.vectors / np.linalg.norm(self.vectors, axis=1)[:, np.newaxis]
        similarities = np.dot(self.vectors, query_vector)
        
        # Get top k indices
        top_k_indices = np.argsort(similarities)[::-1][:k]
        
        results = []
        for idx in top_k_indices:
            doc = self.documents[idx]
            # Attach score for reranking purposes
            doc.metadata['score'] = float(similarities[idx])
            results.append(doc)
            
        return results

    def save_local(self, folder_path: str):
        """Save the vector store to disk."""
        path = Path(folder_path)
        path.mkdir(exist_ok=True)
        
        # Save vectors
        if self.vectors is not None:
            np.save(path / "vectors.npy", self.vectors)
            
        # Save documents
        docs_data = [
            {"page_content": doc.page_content, "metadata": doc.metadata}
            for doc in self.documents
        ]
        with open(path / "documents.json", "w") as f:
            json.dump(docs_data, f)

    @classmethod
    def load_local(cls, folder_path: str, embedding_model):
        """Load the vector store from disk."""
        path = Path(folder_path)
        if not path.exists():
            return None
            
        store = cls(embedding_model)
        
        vec_file = path / "vectors.npy"
        if vec_file.exists():
            store.vectors = np.load(vec_file)
            
        doc_file = path / "documents.json"
        if doc_file.exists():
            with open(doc_file, "r") as f:
                docs_data = json.load(f)
                store.documents = [
                    NativeDocument(page_content=d["page_content"], metadata=d["metadata"])
                    for d in docs_data
                ]
                
        return store


_store = None

def create_vector_store(chunks: list[str]):
    """Create or update the vector store with new chunks."""
    global _store
    docs = [NativeDocument(page_content=c) for c in chunks]

    existing_store = load_vector_store()
    if existing_store:
        existing_store.add_documents(docs)
        _store = existing_store
    else:
        _store = CustomVectorStore(get_embedding_model())
        _store.add_documents(docs)

    _store.save_local(VECTOR_PATH)
    return _store

def load_vector_store():
    """Load the vector store from disk."""
    global _store

    if _store:
        return _store

    if os.path.exists(VECTOR_PATH):
        _store = CustomVectorStore.load_local(VECTOR_PATH, get_embedding_model())
        return _store

    return None