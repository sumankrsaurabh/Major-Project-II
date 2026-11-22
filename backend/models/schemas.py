from typing import List, Optional

from pydantic import BaseModel, Field


SESSION_ID_PATTERN = r"^[A-Za-z0-9_-]{1,64}$"


class QueryRequest(BaseModel):
    workspace_id: str = Field("default", min_length=1, max_length=64, pattern=SESSION_ID_PATTERN)
    question: str = Field(..., min_length=1, max_length=500)
    session_id: Optional[str] = Field(None, min_length=1, max_length=64, pattern=SESSION_ID_PATTERN, description="Opaque session identifier")


class SourceCitation(BaseModel):
    citation_id: str
    document_id: Optional[str] = None
    filename: str
    page_number: Optional[int] = None
    chunk_index: Optional[int] = None
    score: Optional[float] = None


class ChatResponse(BaseModel):
    answer: str
    status: Optional[str] = "success"
    relevant_documents: Optional[int] = None
    confidence: Optional[str] = None
    citations: List[SourceCitation] = Field(default_factory=list)


class WorkspaceDocumentSummary(BaseModel):
    document_id: str
    filename: str
    chunks: int


class DeleteDocumentResponse(BaseModel):
    status: str
    document_id: str
    documents: List[WorkspaceDocumentSummary]


class UploadProgress(BaseModel):
    filename: str
    total_size: int
    uploaded_size: int
    percentage: float
    status: str


class UploadResponse(BaseModel):
    message: str
    document_id: str
    workspace_id: str
    filename: str
    chunks: int
    file_size_mb: float
    status: str


class HealthResponse(BaseModel):
    status: str
    models_loaded: bool
    embedding_model: bool
    llm_model: bool
    answer_engine: str
    generative: bool


class StatusResponse(BaseModel):
    server_status: str
    models_loaded: bool
    pdf_uploaded: bool
    documents: List[WorkspaceDocumentSummary]
    embedding_model: str
    llm_model: str
    answer_engine: str
    generative: bool
    max_file_size_mb: float


class ClearConversationRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=64, pattern=SESSION_ID_PATTERN, description="Opaque session identifier")
    workspace_id: str = Field("default", min_length=1, max_length=64, pattern=SESSION_ID_PATTERN)


class ClearConversationResponse(BaseModel):
    status: str
    message: Optional[str] = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
