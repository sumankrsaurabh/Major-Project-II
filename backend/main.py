import os
import uuid
import logging
import asyncio
import shutil
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from core.pdf_processor import extract_text_async
from core.vector_store import create_vector_store, load_vector_store
from services.rag_service import generate_answer_async
from services.embedding_service import get_embedding_model
from services.llm_service import get_llm
from models.schemas import QueryRequest, UploadProgress
from config import MAX_FILE_SIZE, CHUNK_SIZE, CHUNK_OVERLAP

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Global state for pre-loaded models
app_state = {
    "embedding_model": None,
    "llm_model": None,
    "models_loaded": False
}

# Temporary upload directory
UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: Load models on server start
    Shutdown: Cleanup resources
    """
    # Startup
    logger.info("🚀 Starting server - Loading models...")
    try:
        # Load embedding model
        logger.info("📊 Loading embedding model...")
        app_state["embedding_model"] = get_embedding_model()
        logger.info("✓ Embedding model loaded")
        
        # Load LLM
        logger.info("🤖 Loading LLM model...")
        app_state["llm_model"] = get_llm()
        logger.info("✓ LLM model loaded")
        
        app_state["models_loaded"] = True
        logger.info("✅ All models loaded successfully!")
    except Exception as e:
        logger.error(f"❌ Error loading models: {e}")
        app_state["models_loaded"] = False
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down server...")
    # Cleanup temporary uploads
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)
    logger.info("✓ Cleanup complete")


app = FastAPI(
    title="ChatWithPDF RAG System",
    description="AI-powered PDF Q&A with RAG - Async Support",
    version="2.0",
    lifespan=lifespan
)

# Apply CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "models_loaded": app_state["models_loaded"],
        "embedding_model": app_state["embedding_model"] is not None,
        "llm_model": app_state["llm_model"] is not None
    }


@app.post("/upload")
async def upload(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    """
    Upload and process PDF file with support for large files
    Supports files up to MAX_FILE_SIZE
    """
    if not app_state["models_loaded"]:
        raise HTTPException(500, "Models not loaded. Server may still be initializing.")
    
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files allowed")
    
    # Create unique temp file
    temp_filename = f"{uuid.uuid4().hex}.pdf"
    temp_path = UPLOAD_DIR / temp_filename
    
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Check file size limit
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                413,
                f"File too large. Maximum size: {MAX_FILE_SIZE / (1024**2):.0f}MB"
            )
        
        # Write file to disk
        with open(temp_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"📄 Processing PDF: {file.filename} ({file_size / (1024**2):.2f}MB)")
        
        # Extract text asynchronously
        text = await extract_text_async(str(temp_path))
        
        if not text.strip():
            raise HTTPException(400, "No text extracted from PDF")
        
        # Create chunks
        logger.info(f"📋 Creating chunks (size: {CHUNK_SIZE}, overlap: {CHUNK_OVERLAP})...")
        chunks = []
        for i in range(0, len(text), CHUNK_SIZE - CHUNK_OVERLAP):
            chunk = text[i : i + CHUNK_SIZE]
            if chunk.strip():
                chunks.append(chunk)
        
        logger.info(f"✓ Created {len(chunks)} chunks")
        
        # Create vector store
        logger.info("🔍 Building vector store...")
        await asyncio.to_thread(create_vector_store, chunks)
        logger.info("✓ Vector store created successfully")
        
        # Schedule cleanup
        background_tasks.add_task(cleanup_temp_file, temp_path)
        
        return {
            "message": "PDF processed successfully",
            "filename": file.filename,
            "chunks": len(chunks),
            "file_size_mb": round(file_size / (1024**2), 2),
            "status": "ready"
        }
    
    except HTTPException:
        # Clean up on HTTP errors
        if temp_path.exists():
            temp_path.unlink()
        raise
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(500, f"Upload failed: {str(e)}")


@app.post("/chat")
async def chat(req: QueryRequest):
    """
    Process question and generate answer asynchronously
    """
    if not app_state["models_loaded"]:
        raise HTTPException(500, "Models not loaded")
    
    store = load_vector_store()
    if not store:
        raise HTTPException(400, "No PDF uploaded. Please upload a PDF first.")
    
    try:
        logger.info(f"❓ Question: {req.question}")
        answer_data = await generate_answer_async(req.question)
        logger.info(f"✓ Answer generated ({len(answer_data['answer'])} chars)")
        return answer_data
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(500, f"Failed to generate answer: {str(e)}")


@app.get("/status")
async def status():
    """Get system status"""
    store = load_vector_store()
    return {
        "server_status": "running",
        "models_loaded": app_state["models_loaded"],
        "pdf_uploaded": store is not None,
        "embedding_model": "all-MiniLM-L6-v2",
        "llm_model": "llama-3.3-70b-versatile",
        "max_file_size_mb": MAX_FILE_SIZE / (1024**2)
    }


async def cleanup_temp_file(file_path: Path):
    """Cleanup temporary file"""
    await asyncio.sleep(60)  # Wait 60 seconds before cleanup
    if file_path.exists():
        file_path.unlink()
        logger.info(f"🗑️ Cleaned up temp file: {file_path.name}")
