import numpy as np
import pytest

import core.vector_store as vector_store


class DeterministicEmbeddings:
    def embed_documents(self, texts):
        return [self._vector(text) for text in texts]

    def embed_query(self, text):
        return self._vector(text)

    @staticmethod
    def _vector(text):
        # Deterministic two-dimensional fixture; no model download is required.
        value = sum(ord(char) for char in text) % 100
        return [float(value + 1), float(100 - value)]


@pytest.fixture
def isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setattr(vector_store, "VECTOR_PATH", str(tmp_path / "indexes"))
    monkeypatch.setattr(vector_store, "get_embedding_model", DeterministicEmbeddings)
    vector_store.clear_vector_store_cache()
    yield
    vector_store.clear_vector_store_cache()


def test_workspaces_have_independent_indexes(isolated_storage):
    vector_store.create_vector_store(["private alpha content"], "workspace-alpha")
    vector_store.create_vector_store(["separate beta content"], "workspace-beta")

    alpha = vector_store.load_vector_store("workspace-alpha")
    beta = vector_store.load_vector_store("workspace-beta")

    assert [doc.page_content for doc in alpha.documents] == ["private alpha content"]
    assert [doc.page_content for doc in beta.documents] == ["separate beta content"]


def test_workspace_index_persists_after_cache_clear(isolated_storage):
    vector_store.create_vector_store(["persisted document content"], "workspace-persist")
    vector_store.clear_vector_store_cache()

    restored = vector_store.load_vector_store("workspace-persist")

    assert restored is not None
    assert restored.documents[0].page_content == "persisted document content"


@pytest.mark.parametrize("workspace_id", ["../outside", "nested/name", "a\\b", "", "x" * 65])
def test_invalid_workspace_ids_are_rejected(isolated_storage, workspace_id):
    with pytest.raises(ValueError):
        vector_store.load_vector_store(workspace_id)


def test_missing_workspace_does_not_fall_back_to_another(isolated_storage):
    vector_store.create_vector_store(["default workspace content"], "default")

    assert vector_store.load_vector_store("unrelated-workspace") is None


def test_document_catalog_and_delete_preserve_other_documents(isolated_storage):
    vector_store.create_vector_store(
        ["first document chunk", "first document second chunk"],
        "workspace-docs", "doc-first", "first.pdf",
    )
    vector_store.create_vector_store(
        ["second document chunk"],
        "workspace-docs", "doc-second", "second.pdf",
    )

    catalog = vector_store.list_workspace_documents("workspace-docs")
    assert {item["document_id"] for item in catalog} == {"doc-first", "doc-second"}
    assert next(item for item in catalog if item["document_id"] == "doc-first")["chunks"] == 2

    assert vector_store.delete_workspace_document("workspace-docs", "doc-first") is True
    remaining = vector_store.list_workspace_documents("workspace-docs")
    assert remaining == [{"document_id": "doc-second", "filename": "second.pdf", "chunks": 1}]
    store = vector_store.load_vector_store("workspace-docs")
    assert [doc.page_content for doc in store.documents] == ["second document chunk"]


def test_deleting_last_document_removes_workspace_index(isolated_storage):
    vector_store.create_vector_store(["only document"], "workspace-empty", "doc-only", "only.pdf")
    assert vector_store.delete_workspace_document("workspace-empty", "doc-only") is True
    assert vector_store.load_vector_store("workspace-empty") is None
    assert vector_store.list_workspace_documents("workspace-empty") == []


def test_index_archive_keeps_vectors_and_metadata_together(isolated_storage):
    vector_store.create_vector_store(["atomic archive content"], "workspace-atomic", "doc-atomic", "atomic.pdf")
    archive = vector_store._workspace_path("workspace-atomic") / "index.npz"
    assert archive.is_file()
    vector_store.clear_vector_store_cache()
    restored = vector_store.load_vector_store("workspace-atomic")
    assert restored.documents[0].metadata["document_id"] == "doc-atomic"
    assert restored.vectors.shape[0] == 1
