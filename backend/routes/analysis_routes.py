"""
Advanced Analysis API Endpoints
Exposes all AI/ML/NLP/CV capabilities
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_analysis_services():
    """Construct optional analysis services only when an analysis endpoint is used."""
    from services.comprehensive_analysis_service import ComprehensiveAnalysisService, AdvancedQAService

    comprehensive_service = ComprehensiveAnalysisService()
    return comprehensive_service, AdvancedQAService(comprehensive_service)


# Create router
router = APIRouter(prefix="/analysis", tags=["Analysis"])


# Request/Response Models
class DocumentAnalysisRequest(BaseModel):
    text: str
    detailed: bool = True


class QueryRequest(BaseModel):
    query: str


class ConversationRequest(BaseModel):
    conversation_id: str
    user_query: str
    context_text: str = ""


class TextComparisonRequest(BaseModel):
    text1: str
    text2: str


class AnswerGenerationRequest(BaseModel):
    question: str
    context: str


class AnalysisResponse(BaseModel):
    status: str
    data: Dict
    error: Optional[str] = None


# Endpoints

@router.post("/document", response_model=AnalysisResponse)
async def analyze_document(request: DocumentAnalysisRequest):
    """Comprehensive document analysis with NLP, entities, and key phrases"""
    try:
        comprehensive_service, _ = get_analysis_services()
        result = await comprehensive_service.analyze_document(
            request.text,
            detailed=request.detailed
        )
        return AnalysisResponse(status="success", data=result)
    except Exception as e:
        logger.error(f"Document analysis error: {e}")
        return AnalysisResponse(status="error", data={}, error=str(e))


@router.post("/query", response_model=AnalysisResponse)
async def analyze_query(request: QueryRequest):
    """Analyze user query for intent, question type, and entities"""
    try:
        comprehensive_service, _ = get_analysis_services()
        result = await comprehensive_service.analyze_query(request.query)
        return AnalysisResponse(status="success", data=result)
    except Exception as e:
        logger.error(f"Query analysis error: {e}")
        return AnalysisResponse(status="error", data={}, error=str(e))


@router.post("/insights", response_model=AnalysisResponse)
async def extract_insights(request: DocumentAnalysisRequest):
    """Extract key insights and suggestions from text"""
    try:
        comprehensive_service, _ = get_analysis_services()
        result = await comprehensive_service.extract_insights(request.text)
        return AnalysisResponse(status="success", data=result)
    except Exception as e:
        logger.error(f"Insights extraction error: {e}")
        return AnalysisResponse(status="error", data={}, error=str(e))


@router.post("/conversation", response_model=AnalysisResponse)
async def process_conversation(request: ConversationRequest):
    """Process conversation with context and entity tracking"""
    try:
        comprehensive_service, _ = get_analysis_services()
        result = await comprehensive_service.process_conversation(
            request.conversation_id,
            request.user_query,
            request.context_text
        )
        return AnalysisResponse(status="success", data=result)
    except Exception as e:
        logger.error(f"Conversation processing error: {e}")
        return AnalysisResponse(status="error", data={}, error=str(e))


@router.post("/compare", response_model=AnalysisResponse)
async def compare_texts(request: TextComparisonRequest):
    """Compare two texts for similarities and differences"""
    try:
        comprehensive_service, _ = get_analysis_services()
        result = await comprehensive_service.compare_texts(
            request.text1,
            request.text2
        )
        return AnalysisResponse(status="success", data=result)
    except Exception as e:
        logger.error(f"Text comparison error: {e}")
        return AnalysisResponse(status="error", data={}, error=str(e))


@router.post("/answer", response_model=AnalysisResponse)
async def generate_answer(request: AnswerGenerationRequest):
    """Generate answer with reasoning and confidence"""
    try:
        _, qa_service = get_analysis_services()
        result = await qa_service.generate_answer(
            request.question,
            request.context
        )
        return AnalysisResponse(status="success", data=result)
    except Exception as e:
        logger.error(f"Answer generation error: {e}")
        return AnalysisResponse(status="error", data={}, error=str(e))


@router.get("/health", response_model=AnalysisResponse)
async def health_check():
    """Health check for analysis service"""
    return AnalysisResponse(
        status="healthy",
        data={"message": "Analysis service is running"}
    )


@router.get("/capabilities", response_model=AnalysisResponse)
async def get_capabilities():
    """Get list of available analysis capabilities"""
    capabilities = {
        'nlp': [
            'tokenization',
            'lemmatization',
            'pos_tagging',
            'named_entity_recognition',
            'dependency_parsing',
            'sentiment_analysis',
            'key_phrase_extraction'
        ],
        'computer_vision': [
            'ocr',
            'text_region_detection',
            'document_edge_detection',
            'image_enhancement',
            'deskewing'
        ],
        'machine_learning': [
            'text_classification',
            'document_clustering',
            'anomaly_detection',
            'recommendations',
            'dimensionality_reduction'
        ],
        'ai': [
            'intent_recognition',
            'dialogue_management',
            'knowledge_graphs',
            'reasoning',
            'question_analysis',
            'entity_tracking'
        ]
    }
    return AnalysisResponse(status="success", data=capabilities)
