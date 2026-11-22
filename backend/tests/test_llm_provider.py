"""Configuration tests for the local answer engine selection."""

import services.llm_service as llm_service


def test_extractive_provider_is_explicit_and_non_generative(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "extractive")
    monkeypatch.setattr(llm_service, "_llm_instance", None)

    engine = llm_service.get_llm()

    assert engine.provider == "extractive"
    assert engine.model_name == "extractive-tfidf-v2"


def test_ollama_provider_is_selected_without_remote_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:3b")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    monkeypatch.setattr(llm_service, "_llm_instance", None)

    engine = llm_service.get_llm()

    assert engine.provider == "ollama"
    assert engine.model_name == "qwen2.5:3b"
    assert engine.base_url == "http://127.0.0.1:11434"
