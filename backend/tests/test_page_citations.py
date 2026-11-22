from types import SimpleNamespace

import numpy as np

import core.pdf_processor as pdf_processor
import core.vector_store as vector_store
import services.rag_service as rag_service


class FakePage:
    def __init__(self, text):
        self._text = text

    def extract_text(self):
        return self._text


class FakePDF:
    pages = [FakePage("first page text"), FakePage(None), FakePage("third page text")]

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def test_extract_pages_preserves_original_one_based_page_numbers(monkeypatch):
    monkeypatch.setattr(pdf_processor.pdfplumber, "open", lambda _path: FakePDF())

    assert pdf_processor.extract_pages("sample.pdf") == [
        {"page_number": 1, "text": "first page text"},
        {"page_number": 3, "text": "third page text"},
    ]


class FakeEmbedding:
    def embed_documents(self, texts):
        return np.asarray([[float(index + 1), 1.0] for index, _ in enumerate(texts)], dtype=np.float32)

    def embed_query(self, _text):
        return np.asarray([1.0, 1.0], dtype=np.float32)


def test_create_vector_store_persists_page_metadata(tmp_path, monkeypatch):
    monkeypatch.setattr(vector_store, "VECTOR_PATH", str(tmp_path))
    monkeypatch.setattr(vector_store, "get_embedding_model", FakeEmbedding)

    vector_store.create_vector_store(
        ["page one chunk", "page three chunk"],
        "workspace-a",
        "document-a",
        "report.pdf",
        [{"page_number": 1, "page_chunk_index": 0}, {"page_number": 3, "page_chunk_index": 0}],
    )

    store = vector_store.load_vector_store("workspace-a")
    assert [doc.metadata["page_number"] for doc in store.documents] == [1, 3]
    assert [doc.metadata["chunk_index"] for doc in store.documents] == [0, 1]
    assert all(doc.metadata["document_id"] == "document-a" for doc in store.documents)


def test_generate_answer_returns_grounded_source_metadata(monkeypatch):
    docs = [
        vector_store.NativeDocument(
            "Revenue increased by 12 percent.",
            {
                "document_id": "doc-a",
                "filename": "annual-report.pdf",
                "page_number": 7,
                "chunk_index": 2,
                "score": 0.91,
            },
        ),
        vector_store.NativeDocument(
            "Operating costs remained stable.",
            {
                "document_id": "doc-a",
                "filename": "annual-report.pdf",
                "page_number": 8,
                "chunk_index": 3,
                "score": 0.86,
            },
        ),
    ]

    class FakeStore:
        def similarity_search(self, _query, k):
            return docs[:k]

    class FakeLLM:
        def invoke(self, prompt):
            assert "[S1 | annual-report.pdf | Page 7]" in prompt
            assert "[S2 | annual-report.pdf | Page 8]" in prompt
            return SimpleNamespace(content="Revenue increased by 12 percent [S1]. Unsupported claim [S99].")

    monkeypatch.setattr(rag_service, "load_vector_store", lambda _workspace: FakeStore())
    monkeypatch.setattr(rag_service, "get_llm", FakeLLM)
    monkeypatch.setattr(rag_service, "CONVERSATION_ENABLED", False)
    monkeypatch.setattr(rag_service, "RERANKING_ENABLED", True)

    result = rag_service.generate_answer("What happened to revenue?")

    assert result["status"] == "success"
    assert "[S1]" in result["answer"]
    assert "[S99]" not in result["answer"]
    assert "[source unavailable]" in result["answer"]
    assert result["citations"] == [
        {
            "citation_id": "S1",
            "document_id": "doc-a",
            "filename": "annual-report.pdf",
            "page_number": 7,
            "chunk_index": 2,
            "score": 0.91,
        },
        {
            "citation_id": "S2",
            "document_id": "doc-a",
            "filename": "annual-report.pdf",
            "page_number": 8,
            "chunk_index": 3,
            "score": 0.86,
        },
    ]
