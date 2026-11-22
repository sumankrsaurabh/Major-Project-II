"""Regression tests for API input validation and safe session identifiers."""

import pytest
from pydantic import ValidationError

from models.schemas import (
    ChatResponse, ClearConversationRequest, DeleteDocumentResponse, HealthResponse,
    QueryRequest, StatusResponse, UploadResponse,
)


@pytest.mark.parametrize("session_id", ["session-01", "user_123", "A9"])
def test_query_accepts_safe_session_ids(session_id):
    request = QueryRequest(question="Summarize this PDF", session_id=session_id)
    assert request.session_id == session_id


@pytest.mark.parametrize(
    "session_id",
    ["../secret", "../../etc/passwd", "nested/name", "name\\value", "", "x" * 65],
)
def test_query_rejects_unsafe_session_ids(session_id):
    with pytest.raises(ValidationError):
        QueryRequest(question="Summarize this PDF", session_id=session_id)


def test_query_allows_missing_session_id():
    assert QueryRequest(question="Summarize this PDF").session_id is None


def test_query_rejects_empty_or_oversized_questions():
    with pytest.raises(ValidationError):
        QueryRequest(question="")
    with pytest.raises(ValidationError):
        QueryRequest(question="x" * 501)


def test_clear_conversation_requires_safe_session_id():
    assert ClearConversationRequest(session_id="session-01").session_id == "session-01"
    with pytest.raises(ValidationError):
        ClearConversationRequest(session_id="../outside")


def test_upload_response_requires_server_generated_document_scope():
    response = UploadResponse(
        message="PDF processed",
        document_id="doc-123",
        workspace_id="workspace-123",
        filename="notes.pdf",
        chunks=4,
        file_size_mb=1.25,
        status="ready",
    )
    assert response.document_id == "doc-123"
    assert response.workspace_id == "workspace-123"


def test_workspace_status_contract_includes_document_inventory():
    response = StatusResponse(
        server_status="running",
        models_loaded=True,
        pdf_uploaded=True,
        documents=[{"document_id": "doc-123", "filename": "notes.pdf", "chunks": 4}],
        embedding_model="all-MiniLM-L6-v2",
        llm_model="qwen2.5:3b",
        answer_engine="qwen2.5:3b",
        generative=True,
        max_file_size_mb=500,
    )
    assert response.documents[0].document_id == "doc-123"
    assert response.generative is True


def test_chat_and_delete_response_contracts():
    assert ChatResponse(answer="Answer").status == "success"
    deletion = DeleteDocumentResponse(
        status="deleted",
        document_id="doc-123",
        documents=[],
    )
    assert deletion.status == "deleted"


def test_health_contract_reports_answer_engine_mode():
    health = HealthResponse(
        status="ok",
        models_loaded=True,
        embedding_model=True,
        llm_model=True,
        answer_engine="extractive-tfidf-v2",
        generative=False,
    )
    assert health.generative is False
