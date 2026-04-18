import os
import time
import logging
from functools import lru_cache
from typing import Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from vector_store import load_vector_store

logger = logging.getLogger(__name__)

# Available model providers with their models (in order of preference)
AVAILABLE_MODELS = [
    # Groq - High-performance models (RECOMMENDED)
    {"provider": "groq", "model": "mixtral-8x7b-32768", "api_key_env": "GROQ_API_KEY"},
    {"provider": "groq", "model": "llama-3-70b-versatile", "api_key_env": "GROQ_API_KEY"},
    {"provider": "groq", "model": "llama-2-70b-chat", "api_key_env": "GROQ_API_KEY"},
    {"provider": "groq", "model": "llama-3-8b-8192", "api_key_env": "GROQ_API_KEY"},
    
    # Gemini (Google) - Free tier with limits (fallback)
    {"provider": "gemini", "model": "gemini-2.0-flash", "api_key_env": "GOOGLE_API_KEY"},
    {"provider": "gemini", "model": "gemini-1.5-pro", "api_key_env": "GOOGLE_API_KEY"},
]

# Cache for loaded models
_model_cache: Dict[str, Any] = {}

def get_llm_model(temperature: float = 0.3) -> Optional[Any]:
    """
    Initialize LLM with fallback to available free models.
    Tries providers/models in order of preference until one works.
    
    Supports: Gemini (Google), Groq
    Includes caching to avoid reinitialization.
    """
    model_to_use = os.getenv("LLM_MODEL")
    
    # If env var specifies a model, try it first
    models_to_try = []
    if model_to_use:
        models_to_try.append(model_to_use)
    
    # Add fallback models
    models_to_try.extend([m["model"] for m in AVAILABLE_MODELS])
    
    last_error = None
    for model_name in models_to_try:
        # Check cache first
        cache_key = f"{model_name}:{temperature}"
        if cache_key in _model_cache:
            logger.info(f"Using cached model: {model_name}")
            return _model_cache[cache_key]
        
        # Find model config
        model_config = next((m for m in AVAILABLE_MODELS if m["model"] == model_name), None)
        if not model_config:
            continue
        
        provider = model_config["provider"]
        api_key_env = model_config["api_key_env"]
        
        try:
            logger.info(f"Initializing {provider} model: {model_name}")
            
            if provider == "gemini":
                if not os.getenv(api_key_env):
                    logger.debug(f"Skipping {provider}: {api_key_env} not set")
                    continue
                llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
            elif provider == "groq":
                if not os.getenv(api_key_env):
                    logger.debug(f"Skipping {provider}: {api_key_env} not set")
                    continue
                llm = ChatGroq(
                    model=model_name,
                    temperature=temperature,
                    groq_api_key=os.getenv(api_key_env),
                    timeout=30  # 30 second timeout
                )
            else:
                continue
            
            logger.info(f"✓ Successfully initialized {provider} model: {model_name}")
            _model_cache[cache_key] = llm
            return llm
        
        except Exception as e:
            last_error = e
            logger.warning(f"Failed to initialize {provider}:{model_name} - {type(e).__name__}: {str(e)[:100]}")
            continue
    
    # If all models fail, raise the last error
    raise Exception(f"Could not initialize any LLM model. Last error: {last_error}")

def validate_response(response: str, question: str) -> bool:
    """Validate that response is meaningful and not corrupted."""
    if not response or len(response.strip()) < 10:
        return False
    
    # Check for common error patterns
    error_patterns = ["error", "failed", "unable", "cannot", "exception"]
    response_lower = response.lower()[:200]
    
    if any(pattern in response_lower for pattern in error_patterns):
        if "error:" not in response_lower:  # Allow if it's part of answer content
            return False
    
    return True

def process_user_query(
    user_question: str,
    retry_count: int = 0,
    max_retries: int = 2,
    top_k: int = 8
) -> Dict[str, Any]:
    """
    Processes user query and returns response with citations.
    
    Optimized for:
    - Faster processing with reduced retry attempts
    - Better context retrieval with more chunks (top_k=8)
    - Efficient vector search
    - Improved source attribution
    """
    
    vector_store = load_vector_store()
    if not vector_store:
        logger.warning("No vector store available")
        return {
            "answer": "No document has been uploaded yet. Please upload a PDF first.",
            "sources": [],
            "status": "no_document"
        }
    
    try:
        # Enhanced retriever optimized for speed and quality
        retriever = vector_store.as_retriever(
            search_type="similarity",  # Default similarity search is fastest
            search_kwargs={
                "k": top_k,  # Get more chunks for better context (8 chunks)
                "score_threshold": 0.5,  # Filter low-confidence matches
            }
        )
        
        # Improved prompt with better instructions
        prompt_template = """
You are an expert at answering questions based on provided context. Follow these rules:

1. Answer ONLY using information from the provided context
2. If the answer is not in the context, say: "The answer is not available in the provided document"
3. Be concise and accurate
4. If asked something complex, break it into clear steps
5. Do not make up or assume information

Context:
{context}

Question: {question}

Answer:"""
        
        prompt = PromptTemplate.from_template(prompt_template)
        model = get_llm_model(temperature=0.2)  # Lower temperature for more consistent answers
        
        def format_docs(docs):
            """Format documents efficiently for context."""
            if not docs:
                return ""
            # Simplified format for faster processing
            return "\n---\n".join([doc.page_content for doc in docs])
        
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | model
            | StrOutputParser()
        )
        
        # Get documents for citations
        docs = retriever.invoke(user_question)
        
        if not docs:
            logger.warning("No relevant documents found")
            return {
                "answer": "I could not find relevant information in the document to answer this question.",
                "sources": [],
                "status": "no_context"
            }
        
        # Generate response
        response = rag_chain.invoke(user_question)
        
        # Validate response
        if not validate_response(response, user_question):
            logger.warning(f"Response validation failed: {response[:100]}")
            if retry_count < max_retries:
                logger.info(f"Retrying... (Attempt {retry_count + 1}/{max_retries})")
                time.sleep(1)
                return process_user_query(user_question, retry_count + 1, max_retries, top_k)
        
        # Format sources with better metadata
        sources = []
        for doc in docs:
            source_text = doc.page_content.strip()
            if len(source_text) > 300:
                source_text = source_text[:300] + "..."
            
            sources.append({
                "content": source_text,
                "metadata": doc.metadata if hasattr(doc, 'metadata') else {}
            })
        
        logger.info(f"✓ Successfully answered question with {len(sources)} sources")
        
        return {
            "answer": response,
            "sources": sources,
            "status": "success",
            "confidence": "high" if len(docs) >= 3 else "medium"
        }
    
    except Exception as e:
        error_str = str(e)
        
        # Handle rate limit errors with retry logic
        if any(term in error_str.lower() for term in ["rate", "429", "quota", "resource_exhausted", "too_many"]):
            if retry_count < max_retries:
                retry_delay = min(5 * (2 ** retry_count), 30)
                logger.warning(f"Rate limited. Retrying in {retry_delay}s... (Attempt {retry_count + 1}/{max_retries})")
                time.sleep(retry_delay)
                return process_user_query(user_question, retry_count + 1, max_retries)
            else:
                logger.error("Max retries exceeded for rate limit")
                return {
                    "answer": "API rate limit exceeded. Please wait a moment and try again.",
                    "sources": [],
                    "error": "RATE_LIMIT_EXCEEDED",
                    "status": "error"
                }
        
        # Handle API key errors
        if "api" in error_str.lower() or "key" in error_str.lower() or "auth" in error_str.lower():
            logger.error(f"API/Auth error: {error_str[:200]}")
            return {
                "answer": "Authentication error. Please check your API keys.",
                "sources": [],
                "error": "AUTH_ERROR",
                "status": "error"
            }
        
        # Handle other errors
        logger.error(f"Error during RAG: {error_str}", exc_info=True)
        return {
            "answer": "Sorry, I encountered an error processing your question. Please try again.",
            "sources": [],
            "error": "INTERNAL_ERROR",
            "status": "error"
        }
