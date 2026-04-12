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


class SectionResult(BaseModel):
    title: str
    preview: str
    relevance: float


class PdfResult(BaseModel):
    name: str
    summary: str
    key_insights: List[str]
    key_phrases: List[str]
    sections: List[SectionResult]
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
    context: str
