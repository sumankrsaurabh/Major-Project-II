import os
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from pdf_processor import extract_text_from_pdf, get_text_chunks
from vector_store import get_vector_store, initialize_embeddings
from llm_manager import process_user_query

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Global state
app_state = {"vector_store_ready": False}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown."""
    # Startup
    try:
        initialize_embeddings()
        app_state["vector_store_ready"] = True
        logger.info("✓ Server initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
    yield
    # Shutdown
    logger.info("Server shutting down...")

app = FastAPI(title="Chat With PDF API", lifespan=lifespan)

# Middleware
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500, description="Question about the document")

class HealthResponse(BaseModel):
    status: str
    ready: bool

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "ready": app_state["vector_store_ready"]
    }

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process PDF file."""
    
    # Validate file
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Check file size (50MB max)
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large. Maximum size: 50MB")
    
    temp_file_path = f"temp_{file.filename}"
    
    try:
        # Write file (using sync operations which is fine in async context for I/O)
        with open(temp_file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"Processing PDF: {file.filename}")
        
        # Extract text
        raw_text = extract_text_from_pdf(temp_file_path)
        if not raw_text or not raw_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF. Try: 1) Different PDF, 2) OCR service for scanned PDFs"
            )
        
        if len(raw_text) > 5000000:  # 5MB text limit
            logger.warning(f"PDF text exceeds 5MB, truncating")
            raw_text = raw_text[:5000000]
        
        # Process chunks
        text_chunks = get_text_chunks(raw_text)
        if not text_chunks:
            raise HTTPException(status_code=400, detail="No valid text chunks extracted")
        
        # Create vector store
        get_vector_store(text_chunks)
        
        logger.info(f"✓ Successfully processed: {file.filename} ({len(text_chunks)} chunks)")
        return {
            "message": "PDF uploaded and processed successfully",
            "chunks_created": len(text_chunks),
            "text_length": len(raw_text)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)[:100]}")
    finally:
        # Cleanup temp file
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")



@app.post("/chat")
async def chat_with_pdf(request: QueryRequest):
    """Process user query and return answer with sources."""
    
    question = request.question.strip()
    
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if not app_state["vector_store_ready"]:
        raise HTTPException(status_code=503, detail="Server not ready. Try again in a moment.")
    
    try:
        response_dict = process_user_query(question)
        
        # Ensure response has all required fields
        response_dict.setdefault("answer", "No response generated")
        response_dict.setdefault("sources", [])
        
        return response_dict
    
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        return {
            "answer": "Sorry, I couldn't process your question. Please try again or rephrase your question.",
            "sources": [],
            "error": "internal_error"
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENV", "development") == "development"
    )
