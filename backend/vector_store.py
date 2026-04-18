from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
import os
import warnings
import logging
import pickle
import hashlib

logger = logging.getLogger(__name__)

# Suppress harmless BERT warnings
warnings.filterwarnings("ignore", message=".*embeddings.position_ids.*")

VECTOR_STORE_PATH = "faiss_index"
CACHE_PATH = "embedding_cache"
# Use faster, smaller model for better performance
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # Fast & accurate

# Global cache for the SentenceTransformer model (loaded only once at startup)
_model_cache = None
_vector_store_cache = None

class DirectSentenceTransformerEmbeddings(Embeddings):
    """Direct wrapper around SentenceTransformer for better compatibility and speed."""
    
    def __init__(self, model_name: str = MODEL_NAME):
        global _model_cache
        
        if _model_cache is None:
            raise RuntimeError("Model not initialized. Call initialize_embeddings() on server startup.")
        
        self.model = _model_cache
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of documents with batch processing.
        
        Optimized for large batches:
        - Uses batch size of 32 for optimal performance
        - Converts to numpy for faster operations
        - Disables progress bar for logs
        """
        batch_size = 32
        all_embeddings = []
        
        # Process in batches for memory efficiency
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.model.encode(
                batch, 
                convert_to_numpy=True,  # Numpy is faster for large batches
                show_progress_bar=False,
                batch_size=batch_size
            )
            all_embeddings.extend(embeddings)
        
        return all_embeddings
    
    def embed_query(self, text: str) -> list[float]:
        """Embed a single query."""
        return self.model.encode(text, convert_to_numpy=False)

def initialize_embeddings():
    """
    Initialize the embedding model - call this once on server startup.
    Automatically selects best available device (GPU if available, otherwise CPU).
    """
    global _model_cache
    if _model_cache is None:
        try:
            logger.info(f"Loading SentenceTransformer model: {MODEL_NAME}")
            
            # Determine best device
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")
            
            _model_cache = SentenceTransformer(
                MODEL_NAME,
                device=device
            )
            logger.info(f"✓ Model loaded successfully on {device}")
        except Exception as e:
            logger.error(f"Failed to load embeddings model: {e}")
            # Try CPU as fallback
            try:
                logger.info("Attempting CPU fallback...")
                _model_cache = SentenceTransformer(MODEL_NAME, device="cpu")
                logger.info("✓ Model loaded on CPU (fallback)")
            except Exception as cpu_error:
                logger.error(f"CPU fallback failed: {cpu_error}")
                raise
    else:
        logger.info(f"✓ Model already loaded")

def get_embeddings():
    """Get embeddings model - uses pre-loaded cached SentenceTransformer."""
    return DirectSentenceTransformerEmbeddings(model_name=MODEL_NAME)

def get_vector_store(text_chunks: list[str]):
    """
    Generates embeddings and stores them in FAISS with persistence.
    Optimized for batch processing of large documents.
    """
    global _vector_store_cache
    
    if not text_chunks:
        raise ValueError("No text chunks provided")
    
    try:
        embeddings = get_embeddings()
        logger.info(f"Creating vector store from {len(text_chunks)} chunks")
        logger.info(f"Generating embeddings (batch size: 32)...")
        
        # Use batch processing for faster embedding generation
        # FAISS.from_texts will handle batching, but we can speed it up
        import time
        start_time = time.time()
        
        vector_store = FAISS.from_texts(
            text_chunks, 
            embedding=embeddings,
            batch_size=32  # Process 32 chunks at a time
        )
        
        # Save to disk for persistence
        vector_store.save_local(VECTOR_STORE_PATH)
        _vector_store_cache = vector_store
        
        elapsed = time.time() - start_time
        logger.info(f"✓ Vector store created and saved to {VECTOR_STORE_PATH}")
        logger.info(f"  Time: {elapsed:.2f}s | Chunks: {len(text_chunks)} | Speed: {len(text_chunks)/elapsed:.1f} chunks/sec")
        return vector_store
    except Exception as e:
        logger.error(f"Error creating vector store: {e}", exc_info=True)
        raise

def load_vector_store():
    """
    Loads the FAISS index from local storage with caching.
    Returns None if no index exists.
    """
    global _vector_store_cache
    
    # Return cached version if available
    if _vector_store_cache is not None:
        return _vector_store_cache
    
    embeddings = get_embeddings()
    
    if os.path.exists(VECTOR_STORE_PATH):
        try:
            logger.info(f"Loading vector store from {VECTOR_STORE_PATH}")
            vector_store = FAISS.load_local(
                VECTOR_STORE_PATH,
                embeddings,
                allow_dangerous_deserialization=True
            )
            _vector_store_cache = vector_store
            logger.info(f"✓ Vector store loaded successfully")
            return vector_store
        except Exception as e:
            logger.error(f"Error loading vector store: {e}", exc_info=True)
            return None
    
    logger.warning("No vector store found")
    return None

def clear_vector_store():
    """Clear the vector store cache and files."""
    global _vector_store_cache
    _vector_store_cache = None
    
    if os.path.exists(VECTOR_STORE_PATH):
        try:
            import shutil
            shutil.rmtree(VECTOR_STORE_PATH)
            logger.info("✓ Vector store cleared")
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
