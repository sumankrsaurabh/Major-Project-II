"""
Advanced Features Service
Integrates NLP, CV, ML, and AI for comprehensive text analysis
"""

import logging
import asyncio
from typing import Dict, List, Optional, Tuple
import numpy as np
from core.nlp_processor import NLPPipeline, AdvancedTokenizer, NamedEntityRecognizer
from core.computer_vision import OCRProcessor, ImageProcessor, DocumentAnalyzer
from core.machine_learning import (
    TextClassifier, DocumentClustering, AnomalyDetector,
    RecommendationEngine, DimensionalityReduction
)
from core.ai_engine import (
    IntentRecognizer, DialogueManager, KnowledgeGraph,
    ReasoningEngine, QuestionAnalyzer
)

logger = logging.getLogger(__name__)


class ComprehensiveAnalysisService:
    """Comprehensive text and document analysis"""
    
    def __init__(self):
        # NLP Components
        self.nlp_pipeline = NLPPipeline()
        self.tokenizer = AdvancedTokenizer()
        self.ner = NamedEntityRecognizer()
        
        # CV Components
        self.ocr = OCRProcessor()
        self.image_processor = ImageProcessor()
        self.doc_analyzer = DocumentAnalyzer()
        
        # ML Components
        self.classifier = TextClassifier()
        self.clustering = DocumentClustering(n_clusters=5)
        self.anomaly_detector = AnomalyDetector()
        self.recommender = RecommendationEngine()
        
        # AI Components
        self.intent_recognizer = IntentRecognizer()
        self.dialogue_manager = DialogueManager()
        self.knowledge_graph = KnowledgeGraph()
        self.reasoning_engine = ReasoningEngine()
        self.question_analyzer = QuestionAnalyzer()
        
        logger.info("✅ Comprehensive Analysis Service initialized")
    
    async def analyze_document(self, text: str, detailed: bool = True) -> Dict:
        """Comprehensive document analysis"""
        try:
            # NLP Analysis
            nlp_results = self.nlp_pipeline.process_text(text, detailed=detailed)
            
            # Key phrases
            key_phrases = self.nlp_pipeline.extract_key_phrases(text, n=15)
            
            # Entity relations
            ner_results = self.ner.recognize_entities(text)
            entity_relations = self.ner.extract_entity_relations(text)
            
            # Sentiment (if available through semantic service)
            
            return {
                'nlp_analysis': nlp_results,
                'key_phrases': key_phrases,
                'entities': ner_results,
                'entity_relations': entity_relations,
                'text_length': len(text),
                'sentence_count': len(nlp_results['sentences']),
                'token_count': len(nlp_results['tokens'])
            }
        except Exception as e:
            logger.error(f"Document analysis error: {e}")
            return {'error': str(e)}
    
    async def analyze_query(self, query: str) -> Dict:
        """Analyze user query for better response"""
        try:
            # Intent recognition
            primary_intent, confidence = self.intent_recognizer.recognize_intent(query)
            all_intents = self.intent_recognizer.recognize_intents(query)
            
            # Question analysis
            if '?' in query:
                question_analysis = self.question_analyzer.analyze_question(query)
            else:
                question_analysis = None
            
            # NLP analysis of query
            nlp_analysis = self.nlp_pipeline.process_text(query, detailed=False)
            
            # Entity extraction from query
            entities = self.ner.recognize_entities(query)
            
            return {
                'primary_intent': primary_intent,
                'intent_confidence': confidence,
                'all_intents': all_intents,
                'question_analysis': question_analysis,
                'nlp_analysis': nlp_analysis,
                'entities': entities
            }
        except Exception as e:
            logger.error(f"Query analysis error: {e}")
            return {'error': str(e)}
    
    async def extract_insights(self, text: str) -> Dict:
        """Extract key insights from text"""
        try:
            sentences = self.tokenizer.tokenize_sentences(text)
            
            insights = {
                'summary_worthy_sentences': [],
                'question_suggestions': [],
                'key_entities': [],
                'important_terms': []
            }
            
            # Find key sentences (longer, informative)
            sentence_lengths = [len(s.split()) for s in sentences]
            avg_length = np.mean(sentence_lengths) if sentence_lengths else 0
            
            for sent in sentences:
                if len(sent.split()) > avg_length * 1.2:
                    insights['summary_worthy_sentences'].append(sent)
            
            # Generate question suggestions
            for entity in list(self.ner.recognize_entities(text).get('PERSON', []))[:3]:
                insights['question_suggestions'].append(f"Who is {entity}?")
                insights['key_entities'].append(entity)
            
            # Important terms
            key_phrases = self.nlp_pipeline.extract_key_phrases(text, n=10)
            insights['important_terms'] = [phrase for phrase, score in key_phrases]
            
            return insights
        except Exception as e:
            logger.error(f"Insight extraction error: {e}")
            return {'error': str(e)}
    
    async def process_conversation(self, conversation_id: str, user_query: str, 
                                  context_text: str = "") -> Dict:
        """Process conversation with context"""
        try:
            # Track conversation
            self.dialogue_manager.add_turn(conversation_id, 'user', user_query)
            
            # Analyze query in context
            query_analysis = await self.analyze_query(user_query)
            
            # Update knowledge graph with entities from context
            entities = self.ner.recognize_entities(context_text)
            for entity_type, entity_list in entities.items():
                for entity in entity_list:
                    self.knowledge_graph.add_entity(entity, entity_type)
            
            # Update dialogue context
            self.dialogue_manager.update_entity_context(
                conversation_id,
                set().union(*entities.values())
            )
            
            return {
                'conversation_id': conversation_id,
                'query_analysis': query_analysis,
                'context': self.dialogue_manager.get_conversation_context(conversation_id),
                'tracked_entities': list(self.dialogue_manager.get_entity_context(conversation_id))
            }
        except Exception as e:
            logger.error(f"Conversation processing error: {e}")
            return {'error': str(e)}
    
    async def compare_texts(self, text1: str, text2: str) -> Dict:
        """Compare two texts"""
        try:
            # Analyze both texts
            analysis1 = self.nlp_pipeline.process_text(text1)
            analysis2 = self.nlp_pipeline.process_text(text2)
            
            # Extract entities
            entities1 = self.ner.recognize_entities(text1)
            entities2 = self.ner.recognize_entities(text2)
            
            # Get key phrases
            phrases1 = self.nlp_pipeline.extract_key_phrases(text1, n=10)
            phrases2 = self.nlp_pipeline.extract_key_phrases(text2, n=10)
            
            phrases1_set = {p[0] for p in phrases1}
            phrases2_set = {p[0] for p in phrases2}
            
            return {
                'text1_stats': {
                    'length': len(text1),
                    'sentences': len(analysis1['sentences']),
                    'tokens': len(analysis1['tokens']),
                    'entities': {k: len(v) for k, v in entities1.items()},
                    'key_phrases': phrases1_set
                },
                'text2_stats': {
                    'length': len(text2),
                    'sentences': len(analysis2['sentences']),
                    'tokens': len(analysis2['tokens']),
                    'entities': {k: len(v) for k, v in entities2.items()},
                    'key_phrases': phrases2_set
                },
                'similarities': {
                    'common_phrases': list(phrases1_set & phrases2_set),
                    'unique_to_text1': list(phrases1_set - phrases2_set),
                    'unique_to_text2': list(phrases2_set - phrases1_set)
                }
            }
        except Exception as e:
            logger.error(f"Text comparison error: {e}")
            return {'error': str(e)}


class AdvancedQAService:
    """Advanced Question Answering with context awareness"""
    
    def __init__(self, comprehensive_service: ComprehensiveAnalysisService):
        self.analysis_service = comprehensive_service
        self.question_analyzer = QuestionAnalyzer()
    
    async def generate_answer(self, question: str, context: str) -> Dict:
        """Generate answer with reasoning"""
        try:
            # Analyze question
            question_analysis = self.question_analyzer.analyze_question(question)
            
            # Analyze context
            context_analysis = await self.analysis_service.analyze_document(context, detailed=False)
            
            # Extract answer candidates from context
            sentences = question_analysis.get('key_terms', [])
            answer_candidates = self._find_answer_candidates(question, context)
            
            return {
                'question': question,
                'question_analysis': question_analysis,
                'answer_candidates': answer_candidates[:3],  # Top 3 candidates
                'context_relevance': self._calculate_relevance(question, context),
                'confidence': self._calculate_confidence(question, context_analysis)
            }
        except Exception as e:
            logger.error(f"QA generation error: {e}")
            return {'error': str(e)}
    
    def _find_answer_candidates(self, question: str, context: str) -> List[str]:
        """Find potential answers in context"""
        sentences = context.split('. ')
        scored_sentences = []
        
        question_words = set(question.lower().split())
        
        for sent in sentences:
            sent_words = set(sent.lower().split())
            overlap = len(question_words & sent_words)
            scored_sentences.append((sent.strip(), overlap))
        
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        return [sent for sent, score in scored_sentences if score > 0]
    
    def _calculate_relevance(self, question: str, context: str) -> float:
        """Calculate relevance of context to question"""
        q_words = set(question.lower().split())
        c_words = set(context.lower().split())
        
        overlap = len(q_words & c_words)
        max_words = max(len(q_words), len(c_words))
        
        return min(overlap / max(max_words, 1), 1.0)
    
    def _calculate_confidence(self, question: str, context_analysis: Dict) -> float:
        """Calculate confidence in answer quality"""
        # More entities and longer text = higher confidence
        entities_count = sum(len(v) for v in context_analysis.get('entities', {}).values())
        token_count = context_analysis.get('token_count', 0)
        
        confidence = min((entities_count + token_count / 100) / 20, 1.0)
        return confidence
