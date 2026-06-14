"""
Artificial Intelligence Module
Intent recognition, dialogue management, reasoning, knowledge graphs
"""

import logging
from typing import List, Dict, Tuple, Optional, Set
import re
from collections import defaultdict, Counter
import json

logger = logging.getLogger(__name__)


class IntentRecognizer:
    """Recognize user intents from queries"""
    
    def __init__(self):
        self.intent_patterns = {
            'summarization': [
                r'\b(summarize|summary|brief|overview|tldr|gist)\b',
                r'\b(what is|what\'s).*(summary|overview|brief)\b',
                r'\b(give|provide).*(summary|overview)\b'
            ],
            'question_answering': [
                r'^\s*what\s+',
                r'^\s*who\s+',
                r'^\s*where\s+',
                r'^\s*when\s+',
                r'^\s*why\s+',
                r'^\s*how\s+',
                r'\?$'
            ],
            'clarification': [
                r'\b(clarify|explain|elaborate|what do you mean)\b',
                r'\b(can you|could you).*(explain|elaborate)\b'
            ],
            'extraction': [
                r'\b(extract|extract all|list|find all|identify)\b',
                r'\b(show me|give me).*(all|list of)\b'
            ],
            'analysis': [
                r'\b(analyze|analysis|analyze the|compare)\b',
                r'\b(what.*differences|what.*similarities)\b'
            ],
            'action': [
                r'\b(translate|convert|transform)\b'
            ],
            'sentiment': [
                r'\b(sentiment|tone|feeling|emotion)\b',
                r'\b(how.*feel|express.*feeling)\b'
            ],
            'entity_recognition': [
                r'\b(find all.*names|list.*entities|extract.*entities)\b'
            ],
            'general': []  # Default fallback
        }
        
        self.intent_confidence = {}
    
    def recognize_intent(self, query: str) -> Tuple[str, float]:
        """Recognize primary intent and confidence"""
        query_lower = query.lower()
        max_confidence = 0.0
        primary_intent = 'general'
        
        for intent, patterns in self.intent_patterns.items():
            if not patterns:  # Skip general
                continue
            
            matched_patterns = sum(1 for pattern in patterns if re.search(pattern, query_lower, re.IGNORECASE))
            
            if matched_patterns > 0:
                confidence = min(matched_patterns / len(patterns), 1.0) if patterns else 0.5
                
                if confidence > max_confidence:
                    max_confidence = confidence
                    primary_intent = intent
        
        self.intent_confidence[query] = (primary_intent, max_confidence)
        return primary_intent, max_confidence
    
    def recognize_intents(self, query: str) -> List[Tuple[str, float]]:
        """Recognize all possible intents ranked by confidence"""
        query_lower = query.lower()
        intents = []
        
        for intent, patterns in self.intent_patterns.items():
            matched_patterns = sum(1 for pattern in patterns if re.search(pattern, query_lower, re.IGNORECASE))
            
            if matched_patterns > 0 or intent == 'general':
                confidence = min(matched_patterns / len(patterns), 1.0) if patterns else 0.1
                intents.append((intent, confidence))
        
        intents.sort(key=lambda x: x[1], reverse=True)
        return intents
    
    def get_intent_explanation(self, intent: str) -> str:
        """Get human-readable explanation of intent"""
        explanations = {
            'summarization': 'User wants a summary or overview of the content',
            'question_answering': 'User is asking a specific question',
            'clarification': 'User wants clarification or more details',
            'extraction': 'User wants to extract or list specific items',
            'analysis': 'User wants comparative or analytical insights',
            'action': 'User wants to transform or convert content',
            'sentiment': 'User wants sentiment or emotional analysis',
            'entity_recognition': 'User wants to identify named entities',
            'general': 'General information request'
        }
        return explanations.get(intent, 'Unknown intent')


class DialogueManager:
    """Manage multi-turn conversations"""
    
    def __init__(self):
        self.conversation_history = {}
        self.context_stack = defaultdict(list)
        self.entity_tracker = defaultdict(set)
    
    def start_conversation(self, conversation_id: str):
        """Start a new conversation"""
        self.conversation_history[conversation_id] = []
        self.context_stack[conversation_id] = []
        self.entity_tracker[conversation_id] = set()
        logger.info(f"Started conversation {conversation_id}")
    
    def add_turn(self, conversation_id: str, speaker: str, text: str, 
                metadata: Optional[Dict] = None):
        """Add a turn to the conversation"""
        if conversation_id not in self.conversation_history:
            self.start_conversation(conversation_id)
        
        turn = {
            'speaker': speaker,
            'text': text,
            'metadata': metadata or {}
        }
        self.conversation_history[conversation_id].append(turn)
    
    def get_conversation_context(self, conversation_id: str, last_n: int = 5) -> List[Dict]:
        """Get recent conversation context"""
        if conversation_id not in self.conversation_history:
            return []
        
        history = self.conversation_history[conversation_id]
        return history[-last_n:] if history else []
    
    def get_entity_context(self, conversation_id: str) -> Set[str]:
        """Get entities mentioned in conversation"""
        return self.entity_tracker.get(conversation_id, set())
    
    def update_entity_context(self, conversation_id: str, entities: Set[str]):
        """Update tracked entities"""
        if conversation_id not in self.entity_tracker:
            self.entity_tracker[conversation_id] = set()
        
        self.entity_tracker[conversation_id].update(entities)
    
    def push_context(self, conversation_id: str, context: Dict):
        """Push context onto stack"""
        self.context_stack[conversation_id].append(context)
    
    def pop_context(self, conversation_id: str) -> Optional[Dict]:
        """Pop context from stack"""
        if self.context_stack[conversation_id]:
            return self.context_stack[conversation_id].pop()
        return None
    
    def get_current_context(self, conversation_id: str) -> Optional[Dict]:
        """Get current context without popping"""
        if self.context_stack[conversation_id]:
            return self.context_stack[conversation_id][-1]
        return None
    
    def clear_conversation(self, conversation_id: str):
        """Clear conversation history"""
        if conversation_id in self.conversation_history:
            del self.conversation_history[conversation_id]
        if conversation_id in self.context_stack:
            del self.context_stack[conversation_id]
        if conversation_id in self.entity_tracker:
            del self.entity_tracker[conversation_id]


class KnowledgeGraph:
    """Simple knowledge graph for reasoning"""
    
    def __init__(self):
        self.entities = set()
        self.relations = defaultdict(list)
        self.entity_properties = defaultdict(dict)
    
    def add_entity(self, entity: str, entity_type: str = 'generic'):
        """Add entity to knowledge graph"""
        self.entities.add(entity)
        self.entity_properties[entity]['type'] = entity_type
    
    def add_relation(self, entity1: str, relation: str, entity2: str):
        """Add relation between entities"""
        self.add_entity(entity1)
        self.add_entity(entity2)
        self.relations[entity1].append({'relation': relation, 'entity': entity2})
    
    def get_related_entities(self, entity: str) -> List[Tuple[str, str]]:
        """Get entities related to given entity"""
        return [(r['entity'], r['relation']) for r in self.relations.get(entity, [])]
    
    def find_path(self, entity1: str, entity2: str, max_depth: int = 3) -> Optional[List[str]]:
        """Find connection path between two entities"""
        if entity1 not in self.entities or entity2 not in self.entities:
            return None
        
        visited = set()
        queue = [(entity1, [entity1])]
        
        while queue and len(queue[0][1]) <= max_depth:
            current, path = queue.pop(0)
            if current == entity2:
                return path
            
            visited.add(current)
            for relation_obj in self.relations.get(current, []):
                next_entity = relation_obj['entity']
                if next_entity not in visited:
                    queue.append((next_entity, path + [next_entity]))
        
        return None
    
    def get_entity_info(self, entity: str) -> Dict:
        """Get all information about an entity"""
        return {
            'entity': entity,
            'properties': self.entity_properties.get(entity, {}),
            'relations': self.get_related_entities(entity)
        }


class ReasoningEngine:
    """Simple logical reasoning"""
    
    def __init__(self):
        self.rules = []
        self.facts = set()
    
    def add_rule(self, condition: str, conclusion: str):
        """Add inference rule"""
        self.rules.append({'condition': condition, 'conclusion': conclusion})
    
    def add_fact(self, fact: str):
        """Add a fact"""
        self.facts.add(fact)
    
    def infer(self) -> List[str]:
        """Apply rules to infer new facts"""
        new_facts = set()
        changed = True
        
        while changed:
            changed = False
            for rule in self.rules:
                # Simple pattern matching
                if self._match_condition(rule['condition']):
                    if rule['conclusion'] not in self.facts:
                        new_facts.add(rule['conclusion'])
                        changed = True
        
        self.facts.update(new_facts)
        return list(new_facts)
    
    def _match_condition(self, condition: str) -> bool:
        """Check if condition matches known facts"""
        # Simple keyword-based matching
        condition_words = set(condition.lower().split())
        
        for fact in self.facts:
            fact_words = set(fact.lower().split())
            if condition_words.issubset(fact_words):
                return True
        
        return False
    
    def get_conclusions_for_fact(self, fact: str) -> List[str]:
        """Get all possible conclusions for a fact"""
        conclusions = []
        for rule in self.rules:
            if fact.lower() in rule['condition'].lower():
                conclusions.append(rule['conclusion'])
        return conclusions


class QuestionAnalyzer:
    """Analyze questions for better answering"""
    
    def __init__(self):
        self.question_types = {
            'what': 'definition|fact|description',
            'why': 'reason|cause|explanation',
            'how': 'process|method|procedure',
            'when': 'time|date|temporal',
            'where': 'location|place|spatial',
            'who': 'person|entity|actor',
            'which': 'selection|choice|multiple',
            'yes_no': 'is|are|do|does|did|can|could|will|would|should|must'
        }
    
    def analyze_question(self, question: str) -> Dict:
        """Analyze question structure"""
        question_lower = question.lower().strip()
        
        # Determine question type
        question_type = self._determine_question_type(question_lower)
        
        # Extract key terms
        key_terms = self._extract_key_terms(question_lower)
        
        # Estimate answer length expectation
        answer_length = self._estimate_answer_length(question_type)
        
        return {
            'question_type': question_type,
            'key_terms': key_terms,
            'expected_answer_length': answer_length,
            'complexity': self._calculate_complexity(question_lower),
            'requires_explanation': 'explain' in question_lower or 'why' in question_lower
        }
    
    def _determine_question_type(self, question: str) -> str:
        """Determine the type of question"""
        if re.match(r'^(is|are|do|does|did|can|could|will|would|should|must)', question):
            return 'yes_no'
        
        first_word = question.split()[0] if question.split() else ''
        return first_word.lower() or 'general'
    
    def _extract_key_terms(self, question: str) -> List[str]:
        """Extract key terms from question"""
        # Remove question words and common words
        stop_words = {'what', 'why', 'how', 'when', 'where', 'who', 'which', 'is', 'are', 
                     'do', 'does', 'did', 'can', 'could', 'will', 'would', 'should', 'must',
                     'the', 'a', 'an', 'in', 'on', 'at', 'by', 'with'}
        
        words = question.split()
        key_terms = [w for w in words if w.lower() not in stop_words and len(w) > 2]
        return key_terms
    
    def _estimate_answer_length(self, question_type: str) -> str:
        """Estimate expected answer length"""
        if question_type == 'yes_no':
            return 'short'
        elif question_type == 'what':
            return 'medium'
        elif question_type == 'why':
            return 'long'
        elif question_type == 'how':
            return 'long'
        else:
            return 'medium'
    
    def _calculate_complexity(self, question: str) -> str:
        """Calculate question complexity"""
        word_count = len(question.split())
        has_conjunction = bool(re.search(r'\b(and|or|but)\b', question))
        has_modifier = bool(re.search(r'\b(very|so|extremely|quite)\b', question))
        
        complexity_score = word_count + (3 if has_conjunction else 0) + (2 if has_modifier else 0)
        
        if complexity_score < 10:
            return 'simple'
        elif complexity_score < 20:
            return 'moderate'
        else:
            return 'complex'
