import asyncio
import logging
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from config import CHUNK_OVERLAP, CHUNK_SIZE, MAX_FILE_SIZE
from core.nlp_processor import AdvancedTokenizer
from core.pdf_processor import extract_text_async
from core.vector_store import (
    create_vector_store, delete_workspace_document, list_workspace_documents,
    load_vector_store, validate_document_id, validate_workspace_id,
)
from models.schemas import (\n    ChatResponse, ClearConversationRequest, DeleteDocumentResponse, HealthResponse,\n    QueryRequest, StatusResponse, UploadResponse,\n)
from routes.analysis_routes import router as analysis_router
from services.embedding_service import get_embedding_model
from services.llm_service import get_llm
from services.rag_service import clear_conversation, generate_answer_async

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app_state = {"embedding_model": None, "llm_model": None, "models_loaded": False}
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "temp_uploads"))
UPLOAD_CHUNK_SIZE = 1024 * 1024


@asynccontextmanager
async def lifespan(app: FastAPI):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Starting ChatWithPDF services")
    try:
        app_state["embedding_model"] = get_embedding_model()
        app_state["llm_model"] = get_llm()
        readiness_check = getattr(app_state["llm_model"], "check_ready", None)
        if readiness_check and not readiness_check():
            raise RuntimeError("Configured local generative model is not available in Ollama")
        app_state["models_loaded"] = True
        logger.info("AI services initialized")
    except Exception:
        app_state["models_loaded"] = False
        logger.exception("AI service initialization failed")
    yield
    app_state.update(embedding_model=None, llm_model=None, models_loaded=False)
    # Do not delete the shared upload directory on shutdown: another worker may
    # still be processing a request. Each request owns and removes its own temp file.


app = FastAPI(
    title="ChatWithPDF",
    description="Local-first document question answering",
    version="2.1.0",
    lifespan=lifespan,
)

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(analysis_router, prefix="/api")
app.include_router(analysis_router, prefix="/api/v1")


@app.get("/health", response_model=HealthResponse)
async def health():
    return {
        "status": "ok",
        "models_loaded": app_state["models_loaded"],
        "embedding_model": app_state["embedding_model"] is not None,
        "llm_model": app_state["llm_model"] is not None,
        "answer_engine": getattr(app_state["llm_model"], "model_name", "unavailable"),
        "generative": getattr(app_state["llm_model"], "provider", "extractive") == "ollama",
    }


@app.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...), workspace_id: str = Form("default")):
    if not app_state["models_loaded"]:
        raise HTTPException(status_code=503, detail="AI services are not ready")
    try:
        workspace_id = validate_workspace_id(workspace_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid workspace identifier")

    filename = Path(file.filename or "").name
    if Path(filename).suffix.lower() != ".pdf":
        raise HTTPException(status_code=415, detail="Only PDF files are supported")

    temp_path = UPLOAD_DIR / f"{uuid.uuid4().hex}.pdf"
    file_size = 0
    header = bytearray()

    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        with temp_path.open("wb") as output:
            while chunk := await file.read(UPLOAD_CHUNK_SIZE):
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File exceeds the {MAX_FILE_SIZE // (1024 * 1024)} MB upload limit",
                    )
                if len(header) < 1024:
                    header.extend(chunk[: 1024 - len(header)])
                output.write(chunk)

        if b"%PDF-" not in header:
            raise HTTPException(status_code=415, detail="The uploaded file is not a valid PDF")

        logger.info("Processing PDF upload (%s bytes)", file_size)
        extracted_text = await extract_text_async(str(temp_path))
        if not extracted_text or not extracted_text.strip():
            raise HTTPException(status_code=422, detail="No extractable text found in the PDF")

        tokenizer = AdvancedTokenizer()
        chunks = tokenizer.chunk_text(extracted_text, CHUNK_SIZE, CHUNK_OVERLAP)
        if not chunks:
            raise HTTPException(status_code=422, detail="The PDF did not produce any indexable text")

        document_id = uuid.uuid4().hex
        await asyncio.to_thread(create_vector_store, chunks, workspace_id, document_id, filename)
        return {
            "message": "PDF processed successfully",
            "document_id": document_id,
            "workspace_id": workspace_id,
            "filename": filename,
            "chunks": len(chunks),
            "file_size_mb": round(file_size / (1024**2), 2),
            "status": "ready",
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception("PDF upload or processing failed")
        raise HTTPException(status_code=500, detail="PDF processing failed. Check server logs.")
    finally:
        await file.close()
        temp_path.unlink(missing_ok=True)


@app.delete("/workspaces/{workspace_id}/documents/{document_id}", response_model=DeleteDocumentResponse)
async def delete_document(workspace_id: str, document_id: str):
    try:
        workspace_id = validate_workspace_id(workspace_id)
        document_id = validate_document_id(document_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid workspace or document identifier")

    deleted = await asyncio.to_thread(delete_workspace_document, workspace_id, document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found in this workspace")
    return {
        "status": "deleted",
        "document_id": document_id,
        "documents": list_workspace_documents(workspace_id),
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: QueryRequest):
    if not app_state["models_loaded"]:
        raise HTTPException(status_code=503, detail="AI services are not ready")
    try:
        workspace_id = validate_workspace_id(req.workspace_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid workspace identifier")
    if not load_vector_store(workspace_id):
        raise HTTPException(status_code=409, detail="No PDF has been indexed in this workspace")

    try:
        answer_data = await generate_answer_async(req.question, req.session_id, workspace_id)
        logger.info("Chat response generated (%s characters)", len(answer_data.get("answer", "")))
        return answer_data
    except Exception:
        logger.exception("Chat request failed")
        raise HTTPException(status_code=500, detail="Unable to generate an answer. Check server logs.")


@app.post("/clear-conversation")
async def clear_conversation_endpoint(req: ClearConversationRequest):
    try:
        return clear_conversation(req.session_id)
    except Exception:
        logger.exception("Conversation cleanup failed")
        raise HTTPException(status_code=500, detail="Unable to clear conversation")


@app.get("/status", response_model=StatusResponse)
async def status(workspace_id: str = Query("default", min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")):
    try:
        workspace_id = validate_workspace_id(workspace_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid workspace identifier")
    store = load_vector_store(workspace_id)
    return {
        "server_status": "running",
        "models_loaded": app_state["models_loaded"],
        "pdf_uploaded": store is not None,
        "documents": list_workspace_documents(workspace_id),
        "embedding_model": getattr(app_state["embedding_model"], "model_name", "unavailable"),
        "llm_model": getattr(app_state["llm_model"], "model_name", "unavailable"),
        "answer_engine": getattr(app_state["llm_model"], "model_name", "unavailable"),
        "generative": getattr(app_state["llm_model"], "provider", "extractive") == "ollama",
        "max_file_size_mb": MAX_FILE_SIZE / (1024**2),
    }


# Versioned API surface. Existing routes remain as compatibility aliases during migration.
async def status_v1(workspace_id: str):
    return await status(workspace_id)


app.add_api_route("/api/v1/health", health, methods=["GET"], response_model=HealthResponse, tags=["API v1"])
app.add_api_route("/api/v1/documents/upload", upload, methods=["POST"], response_model=UploadResponse, tags=["API v1"])
app.add_api_route("/api/v1/workspaces/{workspace_id}/documents/{document_id}", delete_document, methods=["DELETE"], response_model=DeleteDocumentResponse, tags=["API v1"])
app.add_api_route("/api/v1/chat", chat, methods=["POST"], response_model=ChatResponse, tags=["API v1"])
app.add_api_route("/api/v1/conversations/clear", clear_conversation_endpoint, methods=["POST"], tags=["API v1"])
app.add_api_route("/api/v1/workspaces/{workspace_id}/status", status_v1, methods=["GET"], response_model=StatusResponse, tags=["API v1"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
