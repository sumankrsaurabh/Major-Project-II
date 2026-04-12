from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from app.services import process_pdfs, answer_question
from app.schemas import UploadResponse, QARequest, QAResponse

app = FastAPI(
    title="Chat With Your PDF",
    description="Upload PDFs to summarize, ask questions, extract images, and explore knowledge with NLP and computer vision.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/upload", response_model=UploadResponse)
async def upload_pdfs(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No PDF files uploaded.")
    return await process_pdfs(files)


@app.post("/api/qa", response_model=QAResponse)
def qa(request: QARequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question is required.")
    return answer_question(request.question, request.document_text)
