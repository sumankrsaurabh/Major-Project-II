from pydantic import BaseModel, Field
from typing import Optional, List

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")

class ChatResponse(BaseModel):
    answer: str
    status: Optional[str] = "success"
    relevant_documents: Optional[int] = None
    confidence: Optional[str] = None

class UploadProgress(BaseModel):
    filename: str
    total_size: int
    uploaded_size: int
    percentage: float
    status: str

class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks: int
    file_size_mb: float
    status: str

class HealthResponse(BaseModel):
    status: str
    models_loaded: bool
    embedding_model: bool
    llm_model: bool

class StatusResponse(BaseModel):
    server_status: str
    models_loaded: bool
    pdf_uploaded: bool
    embedding_model: str
    llm_model: str
    max_file_size_mb: float

class ClearConversationRequest(BaseModel):
    session_id: str

class ClearConversationResponse(BaseModel):
    status: str
    message: Optional[str] = None

