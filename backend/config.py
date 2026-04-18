MODEL_PRIORITY = ["groq", "gemini"]

GROQ_MODEL = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-1.5-flash"

# File upload configuration
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
MAX_REQUEST_SIZE = 600 * 1024 * 1024  # 600 MB

# Chunking configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 5

# Storage
VECTOR_PATH = "faiss_index"

# Performance
REQUEST_TIMEOUT = 120  # seconds
UPLOAD_TIMEOUT = 300  # seconds