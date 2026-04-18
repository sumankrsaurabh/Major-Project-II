MODEL_PRIORITY = ["groq", "gemini"]

GROQ_MODEL = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-1.5-flash"

# File upload configuration
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
MAX_REQUEST_SIZE = 600 * 1024 * 1024  # 600 MB

# Chunking configuration (improved for semantic preservation)
CHUNK_SIZE = 1200  # Larger chunks for better context
CHUNK_OVERLAP = 300  # More overlap for continuity
MIN_CHUNK_SIZE = 100  # Minimum chunk size

# Retrieval configuration (improved accuracy)
TOP_K = 8  # Retrieve more documents for better context
RERANK_TOP_K = 3  # Top-K after reranking
SIMILARITY_THRESHOLD = 0.3  # Minimum similarity score

# Conversation configuration
MAX_HISTORY = 10  # Keep last 10 messages
MAX_CONTEXT_TOKENS = 6000  # Token limit for context

# Storage
VECTOR_PATH = "faiss_index"
CONVERSATION_HISTORY_PATH = "conversations"

# Performance
REQUEST_TIMEOUT = 120  # seconds
UPLOAD_TIMEOUT = 300  # seconds
RESPONSE_TIMEOUT = 60  # seconds

# Quality settings
RERANKING_ENABLED = True  # Enable result reranking
CONVERSATION_ENABLED = True  # Enable chat history
USE_HYDE = True  # Hypothetical Document Embeddings
TEMPERATURE = 0.7  # Model temperature (0-1)
CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for answers