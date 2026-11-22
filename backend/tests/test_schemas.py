import pytest
from pydantic import ValidationError

from models.schemas import ClearConversationRequest, QueryRequest


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
