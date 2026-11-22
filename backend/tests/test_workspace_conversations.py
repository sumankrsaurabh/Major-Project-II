from pathlib import Path

import pytest

import services.rag_service as rag_service
from services.rag_service import ConversationManager


def test_same_session_id_has_isolated_history_per_workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(rag_service, "CONVERSATION_HISTORY_PATH", str(tmp_path))

    first = ConversationManager("shared-session", "workspace-a")
    second = ConversationManager("shared-session", "workspace-b")

    first.add_message("user", "private question A")
    second.add_message("user", "private question B")

    assert "private question A" in first.get_context()
    assert "private question B" not in first.get_context()
    assert "private question B" in second.get_context()
    assert "private question A" not in second.get_context()
    assert first.history_file != second.history_file


def test_clearing_one_workspace_does_not_clear_another(tmp_path, monkeypatch):
    monkeypatch.setattr(rag_service, "CONVERSATION_HISTORY_PATH", str(tmp_path))

    first = ConversationManager("shared-session", "workspace-a")
    second = ConversationManager("shared-session", "workspace-b")
    first.add_message("user", "workspace A")
    second.add_message("user", "workspace B")

    rag_service.clear_conversation("shared-session", "workspace-a")

    assert not first.history_file.exists()
    assert second.history_file.exists()
    assert "workspace B" in ConversationManager("shared-session", "workspace-b").get_context()


def test_invalid_workspace_id_is_rejected_for_conversations(tmp_path, monkeypatch):
    monkeypatch.setattr(rag_service, "CONVERSATION_HISTORY_PATH", str(tmp_path))

    with pytest.raises(ValueError):
        ConversationManager("session", "../outside")
