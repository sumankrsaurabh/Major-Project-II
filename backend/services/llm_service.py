import logging
import re
import math
from collections import Counter
from typing import Optional

logger = logging.getLogger(__name__)

class NativeResponse:
    """A wrapper for LLM responses to mimic expected attributes if needed."""
    def __init__(self, content: str):
        self.content = content
        
    def __str__(self):
        return self.content

class ImprovedLLM:
    """
    Improved local LLM using advanced NLP techniques.
    Generates more accurate and coherent answers through better extraction and synthesis.
    """
    def __init__(self, model_name: str = "improved-local-v2", temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature

    def _extract_query_and_context(self, prompt: str) -> tuple:
        """Extract query and context from structured prompt."""
        query = ""
        context = ""
        
        if "User Question:" in prompt:
            query = prompt.split("User Question:")[1].split("\n")[0].strip()
            
        if "Context from document:" in prompt:
            context_part = prompt.split("Context from document:")[1]
            if "User Question:" in context_part:
                context_part = context_part.split("User Question:")[0]
            context = context_part.strip()
            
        return query, context

    def _split_into_sentences(self, text: str) -> list:
        """Split text into meaningful sentences."""
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
        # Filter out very short sentences and clean up
        sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
        return sentences

    def _score_sentences_improved(self, query: str, sentences: list) -> list:
        """Score sentences using improved TF-IDF with query focus."""
        if not sentences:
            return []
        
        def tokenize(text: str) -> list:
            return re.findall(r'\b\w+\b', text.lower())
        
        query_tokens = set(tokenize(query))
        if not query_tokens:
            return [(0, s) for s in sentences]
        
        # Remove common stop words for better scoring
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'was', 'are', 'be', 'as', 'by'}
        query_tokens = query_tokens - stop_words
        
        scored_sentences = []
        
        for sentence in sentences:
            # Count query term matches
            sentence_lower = sentence.lower()
            match_count = sum(1 for token in query_tokens if token in sentence_lower)
            
            # Prefer longer, more informative sentences
            word_count = len(tokenize(sentence))
            length_score = min(word_count / 50.0, 1.0)  # Normalized to [0, 1]
            
            # Calculate final score
            term_score = match_count / max(len(query_tokens), 1)
            final_score = (0.7 * term_score) + (0.3 * length_score)
            
            scored_sentences.append((final_score, sentence))
        
        # Sort by score descending
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        return scored_sentences

    def _synthesize_answer(self, query: str, scored_sentences: list) -> str:
        """Synthesize coherent answer from top scored sentences."""
        # Select top sentences with good scores
        selected_sentences = []
        seen_content = set()
        
        for score, sentence in scored_sentences:
            if score > 0.15:  # Lowered threshold for more inclusion
                # Avoid near-duplicate sentences
                sentence_hash = hash(sentence[:50])  # Use first 50 chars
                if sentence_hash not in seen_content:
                    selected_sentences.append(sentence)
                    seen_content.add(sentence_hash)
                    if len(selected_sentences) >= 5:  # Get up to 5 sentences
                        break
        
        if not selected_sentences:
            selected_sentences = [scored_sentences[0][1]] if scored_sentences else []
        
        # Build coherent answer
        if selected_sentences:
            # Join with proper punctuation
            answer = " ".join(selected_sentences)
            # Ensure proper ending
            if not answer.endswith(('.',  '!', '?')):
                answer += "."
            return answer
        else:
            return "No relevant information found in the document."

    def invoke(self, prompt: str) -> NativeResponse:
        """
        Generate text based on the provided prompt using improved extraction and synthesis.
        """
        logger.info(f"ImprovedLLM processing prompt (length: {len(prompt)})")
        
        query, context = self._extract_query_and_context(prompt)
        
        if context and query:
            # Split context into sentences
            sentences = self._split_into_sentences(context)
            
            if sentences:
                # Score sentences based on query relevance
                scored_sentences = self._score_sentences_improved(query, sentences)
                
                # Synthesize answer from top sentences
                response_text = self._synthesize_answer(query, scored_sentences)
            else:
                response_text = "The document context appears to be empty or unreadable."
        
        elif "Hypothetical passage:" in prompt:
            # For HyDE, generate a more contextual passage
            try:
                query_match = prompt.split("Question:")
                if len(query_match) > 1:
                    q = query_match[1].split("\n")[0].strip()
                    response_text = f"A comprehensive passage discussing {q}, including relevant details, examples, and context about the topic."
                else:
                    response_text = "A hypothetical detailed passage related to the query."
            except:
                response_text = "A hypothetical passage for semantic retrieval."
        else:
            response_text = "Please provide both a question and document context to generate an answer."
        
        return NativeResponse(response_text)



class OllamaLLM:
    """Local generative model adapter using the Ollama chat HTTP API."""

    def __init__(self, model_name: str, base_url: str, timeout: float = 120.0, temperature: float = 0.2):
        import httpx

        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.temperature = temperature
        self._httpx = httpx

    def invoke(self, prompt: str) -> NativeResponse:
        response = self._httpx.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model_name,
                "stream": False,
                "messages": [{"role": "user", "content": prompt}],
                "options": {"temperature": self.temperature},
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        content = payload.get("message", {}).get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("The local model returned an empty response")
        return NativeResponse(content.strip())


_llm_instance = None


def get_llm():
    """Select an explicitly configured local answer engine."""
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    import os

    provider = os.getenv("LLM_PROVIDER", "extractive").strip().lower()
    if provider == "ollama":
        model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:3b").strip()
        base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip()
        timeout = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
        _llm_instance = OllamaLLM(model_name, base_url, timeout, temperature)
        logger.info("Configured local Ollama generative model: %s", model_name)
    elif provider == "extractive":
        _llm_instance = ImprovedLLM(
            model_name="extractive-tfidf-v2",
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
        )
        logger.warning("Using extractive TF-IDF answer engine; this is not a generative LLM")
    else:
        raise ValueError("Unsupported LLM_PROVIDER. Choose 'ollama' or 'extractive'.")
    return _llm_instance
