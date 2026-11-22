from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def test_upload_pipeline_passes_page_metadata_to_indexer(tmp_path, monkeypatch):
    captured = {}

    async def fake_extract_pages(_path):
        return [
            {"page_number": 1, "text": "alpha content from the first page"},
            {"page_number": 3, "text": "omega content from the third page"},
        ]

    def fake_create_vector_store(chunks, workspace_id, document_id, filename, chunk_metadata):
        captured["chunks"] = chunks
        captured["workspace_id"] = workspace_id
        captured["document_id"] = document_id
        captured["filename"] = filename
        captured["chunk_metadata"] = chunk_metadata

    monkeypatch.setattr(main, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(main, "extract_pages_async", fake_extract_pages)
    monkeypatch.setattr(main, "create_vector_store", fake_create_vector_store)
    monkeypatch.setitem(main.app_state, "models_loaded", True)

    response = client.post(
        "/api/v1/documents/upload",
        data={"workspace_id": "workspace-a"},
        files={"file": ("report.pdf", b"%PDF-1.7 fake pdf bytes", "application/pdf")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["chunks"] == 2
    assert captured["workspace_id"] == "workspace-a"
    assert captured["filename"] == "report.pdf"
    assert len(captured["document_id"]) == 32
    assert captured["chunk_metadata"] == [
        {"page_number": 1, "page_chunk_index": 0},
        {"page_number": 3, "page_chunk_index": 0},
    ]
    assert len(captured["chunks"]) == 2
    assert list(tmp_path.iterdir()) == []
