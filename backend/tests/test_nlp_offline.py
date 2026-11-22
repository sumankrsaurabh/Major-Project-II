"""Offline-safe NLP behavior when optional NLTK corpora are not installed."""

import core.nlp_processor as nlp


def test_tokenizer_falls_back_without_nltk_tokenizer_data(monkeypatch):
    monkeypatch.setattr(nlp, "word_tokenize", lambda _text: (_ for _ in ()).throw(LookupError()))
    monkeypatch.setattr(nlp, "sent_tokenize", lambda _text: (_ for _ in ()).throw(LookupError()))

    tokenizer = nlp.AdvancedTokenizer()

    assert tokenizer.tokenize_words("Hello, local world!") == ["hello", "local", "world"]
    assert tokenizer.tokenize_sentences("First sentence. Second sentence!") == [
        "First sentence.",
        "Second sentence!",
    ]


def test_pos_tagger_falls_back_without_nltk_tagger_data(monkeypatch):
    monkeypatch.setattr(nlp, "pos_tag", lambda _tokens: (_ for _ in ()).throw(LookupError()))

    tagged = nlp.POSTagger().tag_tokens(["running", "useful", "42", "document"])

    assert tagged == [
        ("running", "VBG"),
        ("useful", "JJ"),
        ("42", "CD"),
        ("document", "NN"),
    ]


def test_ner_and_lemmatizer_degrade_gracefully_without_corpora(monkeypatch):
    monkeypatch.setattr(nlp, "word_tokenize", lambda _text: (_ for _ in ()).throw(LookupError()))
    monkeypatch.setattr(nlp, "pos_tag", lambda _tokens: (_ for _ in ()).throw(LookupError()))
    monkeypatch.setattr(nlp, "ne_chunk", lambda _tags: (_ for _ in ()).throw(LookupError()))

    entities = nlp.NamedEntityRecognizer().recognize_entities("Contact team@example.com on 2026-11-22.")
    assert "team@example.com" in entities["EMAIL"]
    assert nlp.Lemmatizer().lemmatize("documents") == "documents"
