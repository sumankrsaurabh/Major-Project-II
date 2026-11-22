import os

# Keep the runtime local-first. Network model providers must be explicitly configured.
MODEL_PRIORITY = [item.strip() for item in os.getenv("MODEL_PRIORITY", "local").split(",") if item.strip()]

# File upload configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_BYTES", str(500 * 1024 * 1024)))
MAX_REQUEST_SIZE = MAX_FILE_SIZE + (10 * 1024 * 1024)

# Chunking configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "300"))
MIN_CHUNK_SIZE = 100

# Retrieval configuration
TOP_K = 8
RERANK_TOP_K = 3
SIMILARITY_THRESHOLD = 0.3

# Conversation configuration
MAX_HISTORY = 10
MAX_CONTEXT_TOKENS = 6000

# Storage
VECTOR_PATH = os.getenv("VECTOR_PATH", "faiss_index")
CONVERSATION_HISTORY_PATH = os.getenv("CONVERSATION_HISTORY_PATH", "conversations")

# Performance
REQUEST_TIMEOUT = 120
UPLOAD_TIMEOUT = 300
RESPONSE_TIMEOUT = 60

# Quality settings
RERANKING_ENABLED = True
CONVERSATION_ENABLED = True
USE_HYDE = False
TEMPERATURE = 0.2
CONFIDENCE_THRESHOLD = 0.5
