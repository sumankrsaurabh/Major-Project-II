import asyncio
import logging
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

from core.vector_store import load_vector_store, validate_workspace_id
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
    
    def __init__(self, session_id: str, workspace_id: str = "default"):
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", session_id or ""):
            raise ValueError("Invalid session identifier")
        self.workspace_id = validate_workspace_id(workspace_id)
        self.session_id = session_id
        base_path = Path(CONVERSATION_HISTORY_PATH)
        self.history_dir = base_path if self.workspace_id == "default" else base_path / "workspaces" / self.workspace_id
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.history_dir / f"{session_id}.json"
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


def generate_answer(query: str, session_id: Optional[str] = None, workspace_id: str = "default"):
    """
    Synchronous answer generation with enhanced accuracy and better retrieval
    """
    store = load_vector_store(workspace_id)

    if not store:
        return {"answer": "No document uploaded. Please upload a PDF first."}

    try:
        # Initialize conversation manager if enabled
        conv_manager = None
        if CONVERSATION_ENABLED and session_id:
            conv_manager = ConversationManager(session_id, workspace_id)

        # Retrieve relevant documents with increased count for better relevance
        logger.info(f"Retrieving {TOP_K} most relevant documents...")
        docs = store.similarity_search(query, k=TOP_K)
        
        if not docs:
            return {"answer": "No relevant information found in the document."}

        # Rerank if enabled - this improves answer quality
        original_doc_count = len(docs)
        if RERANKING_ENABLED:
            docs = rerank_results(query, docs)
            logger.info(f"Reranked from {original_doc_count} to {len(docs)} documents")

        # Build context from documents - improved formatting
        context_parts = []
        citations = []
        for index, doc in enumerate(docs[:RERANK_TOP_K], start=1):
            metadata = getattr(doc, "metadata", {}) or {}
            citation_id = f"S{index}"
            source = {
                "citation_id": citation_id,
                "document_id": metadata.get("document_id"),
                "filename": metadata.get("filename", "Imported document"),
                "page_number": metadata.get("page_number"),
                "chunk_index": metadata.get("chunk_index"),
                "score": metadata.get("score"),
            }
            citations.append(source)
            page_label = f"Page {source['page_number']}" if source["page_number"] else "Page unavailable"
            context_parts.append(
                f"[{citation_id} | {source['filename']} | {page_label}]\n{doc.page_content}"
            )

        context = "\n\n".join(context_parts)

        # Build conversation context if enabled
        conversation_context = ""
        if conv_manager:
            conversation_context = conv_manager.get_context()
            if conversation_context:
                conversation_context = "\n" + conversation_context + "\n"

        # Construct improved prompt with better structure
        prompt = f"""You are an expert AI assistant analyzing the provided document.

Your instructions:
1. Answer the question ONLY using information from the provided context
2. If the exact answer isn't in the context, provide the most relevant information available
3. Be direct and accurate - prioritize clarity over verbosity
4. Cite factual claims using only the source labels [S1], [S2], etc. shown in the context
5. Never invent a source label or page number; the API returns the verified source metadata separately
6. If you cannot find relevant information, clearly state that{conversation_context}
Context from document:
{context}

User Question: {query}

Provide a clear and accurate answer:"""

        # Generate answer using improved LLM
        llm = get_llm()
        response = llm.invoke(prompt)
        answer = response.content if hasattr(response, 'content') else str(response)
        # Do not let a model fabricate citation IDs that were not retrieved.
        allowed_citation_ids = {source["citation_id"] for source in citations}
        answer = re.sub(
            r"\\[(S\\d+)\\]",
            lambda match: match.group(0)
            if match.group(1) in allowed_citation_ids
            else "[source unavailable]",
            answer,
        )

        # Clean up answer if it has redundant prefixes from LLM
        answer = answer.replace("According to your document (analyzed natively via TF-IDF):\n\n", "")

        # Store in conversation history if enabled
        if conv_manager:
            conv_manager.add_message("user", query)
            conv_manager.add_message("assistant", answer)

        # Calculate confidence based on retrieval quality
        confidence = "high" if len(docs) >= RERANK_TOP_K else "medium"
        if any(doc.metadata.get('score', 0) < 0.5 for doc in docs if hasattr(doc, 'metadata')):
            confidence = "low"

        return {
            "answer": answer,
            "status": "success",
            "relevant_documents": len(docs),
            "confidence": confidence,
            "citations": citations,
        }

    except Exception:
        logger.exception("Answer generation failed")
        return {
            "answer": "Unable to generate an answer. Check server logs.",
            "status": "error"
        }


async def generate_answer_async(query: str, session_id: Optional[str] = None, workspace_id: str = "default"):
    """
    Asynchronous answer generation
    Runs in thread pool for non-blocking operation
    """
    try:
        result = await asyncio.to_thread(generate_answer, query, session_id, workspace_id)
        return result
    except Exception:
        logger.exception("Asynchronous answer generation failed")
        return {
            "answer": "Unable to generate an answer. Check server logs.",
            "status": "error"
        }


def clear_conversation(session_id: str, workspace_id: str = "default"):
    """Clear conversation history for one workspace and session."""
    conv_manager = ConversationManager(session_id, workspace_id)
    conv_manager.clear()
    logger.info("Cleared conversation for workspace %s", workspace_id)
    return {"status": "cleared"}

