from pydantic import BaseModel
from typing import List, Optional


class ImageResult(BaseModel):
    name: str
    mime_type: str
    base64: str
    width: Optional[int]
    height: Optional[int]
    ocr_text: Optional[str]


class GraphData(BaseModel):
    labels: List[str]
    values: List[int]


class PdfResult(BaseModel):
    name: str
    summary: str
    key_insights: List[str]
    text: str
    images: List[ImageResult]
    graph_data: GraphData


class UploadResponse(BaseModel):
    documents: List[PdfResult]


class QARequest(BaseModel):
    question: str
    document_text: str


class QAResponse(BaseModel):
    answer: str
    source: str
