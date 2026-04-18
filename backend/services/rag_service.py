import asyncio
import logging
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

from core.vector_store import load_vector_store
from services.llm_service import get_llm
from config import (
    TOP_K, 
    RERANK_TOP_K,
    SIMILARITY_THRESHOLD,
    MAX_HISTORY,
    RERANKING_ENABLED,
    CONVERSATION_ENABLED,
    TEMPERATURE,
    CONFIDENCE_THRESHOLD,
    CONVERSATION_HISTORY_PATH
)

logger = logging.getLogger(__name__)

# Create conversation history directory
Path(CONVERSATION_HISTORY_PATH).mkdir(exist_ok=True)


class ConversationManager:
    """Manage conversation history for context-aware responses"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history_file = Path(CONVERSATION_HISTORY_PATH) / f"{session_id}.json"
        self.messages = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Load conversation history from disk"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading history: {e}")
                return []
        return []
    
    def _save_history(self):
        """Save conversation history to disk"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.messages[-MAX_HISTORY:], f)
        except Exception as e:
            logger.error(f"Error saving history: {e}")
    
    def add_message(self, role: str, content: str):
        """Add message to history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._save_history()
    
    def get_context(self) -> str:
        """Get conversation context for prompt"""
        if not self.messages:
            return ""
        
        context = "Previous conversation:\n"
        for msg in self.messages[-MAX_HISTORY:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content']}\n"
        return context
    
    def clear(self):
        """Clear conversation history"""
        self.messages = []
        if self.history_file.exists():
            self.history_file.unlink()


def rerank_results(query: str, docs: List) -> List:
    """
    Rerank documents using semantic similarity scores
    Keep only top results that meet threshold
    """
    if not RERANKING_ENABLED or len(docs) <= RERANK_TOP_K:
        return docs
    
    try:
        # Filter by similarity threshold
        filtered_docs = [
            doc for doc in docs 
            if hasattr(doc, 'metadata') and doc.metadata.get('score', 1.0) >= SIMILARITY_THRESHOLD
        ]
        
        # Return top-k reranked results
        return filtered_docs[:RERANK_TOP_K] if filtered_docs else docs[:RERANK_TOP_K]
    except Exception as e:
        logger.warning(f"Reranking failed: {e}, returning original docs")
        return docs[:RERANK_TOP_K]


def generate_hyde_query(query: str, llm) -> str:
    """
    Generate hypothetical document embeddings for better retrieval
    """
    try:
        prompt = f"""Generate a hypothetical detailed passage that would answer the following question.

Question: {query}

Hypothetical passage:"""
        
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.warning(f"HyDE generation failed: {e}")
        return query


def generate_answer(query: str, session_id: Optional[str] = None):
    """
    Synchronous answer generation with enhanced accuracy
    """
    store = load_vector_store()

    if not store:
        return {"answer": "No document uploaded. Please upload a PDF first."}

    try:
        # Initialize conversation manager if enabled
        conv_manager = None
        if CONVERSATION_ENABLED and session_id:
            conv_manager = ConversationManager(session_id)

        # Retrieve relevant documents
        logger.info(f"Retrieving {TOP_K} most relevant documents...")
        docs = store.similarity_search(query, k=TOP_K)
        
        if not docs:
            return {"answer": "No relevant information found in the document."}

        # Rerank if enabled
        if RERANKING_ENABLED:
            docs = rerank_results(query, docs)

        # Build context from documents
        context = "\n\n".join([
            f"[Context {i+1}]\n{doc.page_content}" 
            for i, doc in enumerate(docs[:RERANK_TOP_K])
        ])

        # Build conversation context if enabled
        conversation_context = ""
        if conv_manager:
            conversation_context = conv_manager.get_context()

        # Construct enhanced prompt
        prompt = f"""You are an expert AI assistant with deep knowledge of the provided document.
Your goal is to provide accurate, helpful, and well-structured answers.

Instructions:
- Answer ONLY based on the provided context
- If the context doesn't contain relevant information, say so clearly
- Provide detailed and comprehensive answers
- Structure your response clearly with sections if needed
- Be specific and cite the document when relevant

{conversation_context}

Context from document:
{context}

User Question: {query}

Provide a clear, accurate, and comprehensive answer:"""

        # Generate answer
        llm = get_llm()
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, 'content') else str(response)

        # Store in conversation history if enabled
        if conv_manager:
            conv_manager.add_message("user", query)
            conv_manager.add_message("assistant", answer)

        return {
            "answer": answer,
            "status": "success",
            "relevant_documents": len(docs),
            "confidence": "high" if len(docs) >= RERANK_TOP_K else "medium"
        }

    except Exception as e:
        logger.error(f"Answer generation error: {e}")
        return {
            "answer": f"Error generating answer: {str(e)}",
            "status": "error"
        }


async def generate_answer_async(query: str, session_id: Optional[str] = None):
    """
    Asynchronous answer generation
    Runs in thread pool for non-blocking operation
    """
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=4)
    
    try:
        result = await loop.run_in_executor(
            executor,
            generate_answer,
            query,
            session_id
        )
        return result
    except Exception as e:
        logger.error(f"Async answer generation error: {e}")
        return {
            "answer": f"Error: {str(e)}",
            "status": "error"
        }


def clear_conversation(session_id: str):
    """Clear conversation history for a session"""
    try:
        conv_manager = ConversationManager(session_id)
        conv_manager.clear()
        logger.info(f"Cleared conversation for session {session_id}")
        return {"status": "cleared"}
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        return {"status": "error", "message": str(e)}

