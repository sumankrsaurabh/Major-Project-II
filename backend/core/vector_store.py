import os
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from services.embedding_service import get_embedding_model
from config import VECTOR_PATH

_store = None

def create_vector_store(chunks):
    global _store

    docs = [Document(page_content=c) for c in chunks]

    _store = FAISS.from_documents(
        docs,
        embedding=get_embedding_model()
    )

    _store.save_local(VECTOR_PATH)
    return _store


def load_vector_store():
    global _store

    if _store:
        return _store

    if os.path.exists(VECTOR_PATH):
        _store = FAISS.load_local(
            VECTOR_PATH,
            get_embedding_model(),
            allow_dangerous_deserialization=True
        )
        return _store

    return None