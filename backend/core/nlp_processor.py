"""
Advanced NLP Processing Pipeline
Includes tokenization, lemmatization, POS tagging, dependency parsing, NER
"""

import re
import logging
from typing import List, Dict, Tuple, Set, Optional
from collections import Counter, defaultdict
import numpy as np
from nltk.corpus import wordnet
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag, ne_chunk

logger = logging.getLogger(__name__)

# NLTK corpora are optional runtime assets. Never download them during import.

class AdvancedTokenizer:
    """Advanced tokenization with multiple strategies"""
    
    def __init__(self):
        self.sentence_pattern = re.compile(r'[.!?]+')
        self.word_pattern = re.compile(r'\b\w+\b')
        self.punctuation_pattern = re.compile(r'[^\w\s]')
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        try:
            sentences = sent_tokenize(text)
        except LookupError:
            sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def tokenize_words(self, text: str) -> List[str]:
        """Tokenize into words"""
        try:
            return word_tokenize(text.lower())
        except LookupError:
            return self.word_pattern.findall(text.lower())
    
    def tokenize_ngrams(self, text: str, n: int = 2) -> List[Tuple[str, ...]]:
        """Generate n-grams"""
        tokens = self.tokenize_words(text)
        return list(zip(*[tokens[i:] for i in range(n)]))
    
    def remove_stopwords(self, tokens: List[str], custom_stopwords: Set[str] = None) -> List[str]:
        """Remove common stopwords"""
        default_stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        if custom_stopwords:
            default_stopwords.update(custom_stopwords)
        
        return [token for token in tokens if token.lower() not in default_stopwords]

    def chunk_text(self, text: str, chunk_size: int = 1200, overlap: int = 300) -> List[str]:
        """Split text into overlapping chunks of tokens"""
        tokens = self.tokenize_words(text)
        if not tokens:
            return []

        if overlap >= chunk_size:
            overlap = max(chunk_size // 4, 1)

        chunks = []
        start = 0
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunks.append(' '.join(chunk_tokens))
            if end == len(tokens):
                break
            start += chunk_size - overlap

        return chunks


class Lemmatizer:
    """Lemmatization and morphological analysis"""
    
    def __init__(self):
        self.lemma_cache = {}
    
    def lemmatize(self, word: str, pos: str = 'n') -> str:
        """Get lemma for a word"""
        if word in self.lemma_cache:
            return self.lemma_cache[word]
        
        lemma = word
        try:
            synsets = wordnet.synsets(word, pos=self._convert_pos(pos))
            if synsets:
                lemma = synsets[0].lemmas()[0].name()
        except LookupError:
            # Return the surface form when optional WordNet data is unavailable.
            pass
        
        self.lemma_cache[word] = lemma
        return lemma
    
    def _convert_pos(self, pos_tag: str) -> str:
        """Convert POS tag to WordNet format"""
        conversions = {'N': 'n', 'V': 'v', 'J': 'a', 'R': 'r'}
        return conversions.get(pos_tag[0], 'n')
    
    def lemmatize_tokens(self, tokens: List[str], pos_tags: List[Tuple[str, str]] = None) -> List[str]:
        """Lemmatize a list of tokens"""
        if pos_tags is None:
            pos_tags = [(token, 'NN') for token in tokens]
        
        return [self.lemmatize(token, pos) for token, pos in pos_tags]


class POSTagger:
    """Part-of-Speech tagging"""
    
    def __init__(self):
        self.pos_mapping = {
            'NN': 'NOUN', 'NNS': 'NOUN', 'NNP': 'NOUN', 'NNPS': 'NOUN',
            'VB': 'VERB', 'VBD': 'VERB', 'VBG': 'VERB', 'VBN': 'VERB', 'VBP': 'VERB', 'VBZ': 'VERB',
            'JJ': 'ADJ', 'JJR': 'ADJ', 'JJS': 'ADJ',
            'RB': 'ADV', 'RBR': 'ADV', 'RBS': 'ADV',
            'PRP': 'PRON', 'PRP$': 'PRON',
            'DT': 'DET', 'IN': 'ADP', 'CC': 'CCONJ',
        }
    
    def tag_tokens(self, tokens: List[str]) -> List[Tuple[str, str]]:
        """Tag tokens with POS"""
        try:
            return pos_tag(tokens)
        except LookupError:
            # Lightweight fallback keeps local analysis available without downloaded tagger data.
            tagged = []
            for token in tokens:
                if token.endswith(("ing", "ed")):
                    tag = "VBG"
                elif token.isdigit():
                    tag = "CD"
                elif token.endswith(("ous", "ful", "ive", "able")):
                    tag = "JJ"
                else:
                    tag = "NN"
                tagged.append((token, tag))
            return tagged
    
    def get_pos_stats(self, tokens: List[str]) -> Dict[str, int]:
        """Get POS distribution"""
        tagged = self.tag_tokens(tokens)
        pos_counts = Counter()
        for token, pos in tagged:
            pos_type = self.pos_mapping.get(pos, 'OTHER')
            pos_counts[pos_type] += 1
        return dict(pos_counts)


class NamedEntityRecognizer:
    """Named Entity Recognition"""
    
    def __init__(self):
        self.entity_patterns = {
            'EMAIL': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'PHONE': r'\+?1?\d{9,15}',
            'URL': r'https?://[^\s]+',
            'DATE': r'\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2}',
            'TIME': r'\d{1,2}:\d{2}(?::\d{2})?(?:\s?[APap][Mm])?',
            'MONEY': r'\$\d+(?:,\d{3})*(?:\.\d{2})?|£\d+|€\d+',
            'NUMBER': r'\b\d+(?:\.\d+)?\b',
        }
    
    def _tokenize_words(self, text: str) -> List[str]:
        try:
            return word_tokenize(text)
        except LookupError:
            return re.findall(r'\b\w+\b', text)

    def recognize_entities(self, text: str) -> Dict[str, List[str]]:
        """Recognize named entities using patterns and NLTK"""
        entities = defaultdict(list)
        
        # Pattern-based NER
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text)
            entities[entity_type].extend(matches)
        
        # NLTK-based NER
        tokens = self._tokenize_words(text)
        try:
            pos_tags = pos_tag(tokens)
            ne_tree = ne_chunk(pos_tags)
            for subtree in ne_tree:
                if hasattr(subtree, 'label'):
                    entity_type = subtree.label()
                    entity_text = ' '.join(word for word, tag in subtree.leaves())
                    entities[entity_type].append(entity_text)
        except LookupError:
            # Pattern-based entities above remain available without NLTK corpora.
            pass
        
        # Remove duplicates
        return {k: list(set(v)) for k, v in entities.items()}
    
    def extract_entity_relations(self, text: str) -> List[Dict]:
        """Extract relationships between entities"""
        relations = []
        tokens = self._tokenize_words(text)
        try:
            pos_tags = pos_tag(tokens)
        except LookupError:
            pos_tags = POSTagger().tag_tokens(tokens)
        
        for i, (token, pos) in enumerate(pos_tags):
            if pos in ['NN', 'NNP']:  # Nouns
                # Look for relationships (simple heuristic)
                context = tokens[max(0, i-2):min(len(tokens), i+3)]
                relations.append({
                    'entity': token,
                    'pos': pos,
                    'context': ' '.join(context)
                })
        
        return relations


class DependencyParser:
    """Simplified dependency parsing"""
    
    def __init__(self):
        self.dependency_patterns = {
            'subject': r'(\w+)\s+(?:is|are|was|were|be)',
            'object': r'(?:is|are|was|were)\s+(\w+)',
            'action': r'(\w+)\s+(?:and|or)\s+(\w+)',
        }
    
    def parse_dependencies(self, sentence: str) -> List[Dict]:
        """Simple dependency extraction"""
        dependencies = []
        
        for dep_type, pattern in self.dependency_patterns.items():
            matches = re.finditer(pattern, sentence, re.IGNORECASE)
            for match in matches:
                dependencies.append({
                    'type': dep_type,
                    'tokens': match.groups()
                })
        
        return dependencies
    
    def extract_verb_object_pairs(self, tokens: List[str], pos_tags: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """Extract verb-object pairs"""
        pairs = []
        for i, (token, pos) in enumerate(pos_tags):
            if pos.startswith('VB'):  # Verb
                # Look for following noun
                for j in range(i+1, min(i+4, len(pos_tags))):
                    if pos_tags[j][1].startswith('NN'):  # Noun
                        pairs.append((token, pos_tags[j][0]))
                        break
        return pairs


class SyntacticAnalyzer:
    """Analyze syntactic structure of text"""
    
    def __init__(self):
        self.tokenizer = AdvancedTokenizer()
        self.pos_tagger = POSTagger()
        self.parser = DependencyParser()
    
    def analyze_sentence(self, sentence: str) -> Dict:
        """Comprehensive sentence analysis"""
        tokens = self.tokenizer.tokenize_words(sentence)
        pos_tags = self.pos_tagger.tag_tokens(tokens)
        dependencies = self.parser.parse_dependencies(sentence)
        
        return {
            'tokens': tokens,
            'pos_tags': pos_tags,
            'pos_stats': self.pos_tagger.get_pos_stats(tokens),
            'dependencies': dependencies,
            'length': len(tokens),
            'complexity': self._calculate_complexity(tokens, pos_tags)
        }
    
    def _calculate_complexity(self, tokens: List[str], pos_tags: List[Tuple[str, str]]) -> float:
        """Calculate sentence complexity score (0-1)"""
        # More complex = more clauses, more adjectives/adverbs, longer
        complexity_factors = []
        
        # Length factor
        complexity_factors.append(min(len(tokens) / 30, 1.0))
        
        # Clause complexity
        clause_count = sum(1 for _, pos in pos_tags if pos.startswith('VB'))
        complexity_factors.append(min(clause_count / 3, 1.0))
        
        # Modifier density
        modifier_count = sum(1 for _, pos in pos_tags if pos in ['JJ', 'RB', 'JJR', 'JJS', 'RBR', 'RBS'])
        complexity_factors.append(min(modifier_count / len(tokens) * 2, 1.0) if tokens else 0)
        
        return np.mean(complexity_factors)


class NLPPipeline:
    """Complete NLP processing pipeline"""
    
    def __init__(self):
        self.tokenizer = AdvancedTokenizer()
        self.lemmatizer = Lemmatizer()
        self.pos_tagger = POSTagger()
        self.ner = NamedEntityRecognizer()
        self.syntactic_analyzer = SyntacticAnalyzer()
    
    def process_text(self, text: str, detailed: bool = False) -> Dict:
        """Process text through complete pipeline"""
        sentences = self.tokenizer.tokenize_sentences(text)
        
        results = {
            'text': text,
            'sentences': sentences,
            'sentence_count': len(sentences),
            'tokens': self.tokenizer.tokenize_words(text),
            'entities': self.ner.recognize_entities(text),
            'pos_stats': self.pos_tagger.get_pos_stats(self.tokenizer.tokenize_words(text)),
        }
        
        if detailed:
            # Detailed sentence-level analysis
            detailed_sentences = []
            for sent in sentences:
                detailed_sentences.append(self.syntactic_analyzer.analyze_sentence(sent))
            results['detailed_sentences'] = detailed_sentences
        
        return results
    
    def extract_key_phrases(self, text: str, n: int = 10) -> List[Tuple[str, float]]:
        """Extract key phrases with scores"""
        tokens = self.tokenizer.tokenize_words(text)
        tokens = self.tokenizer.remove_stopwords(tokens)
        
        # Noun phrases and named entities are important
        pos_tags = self.pos_tagger.tag_tokens(tokens)
        key_phrases = []
        
        for token, pos in pos_tags:
            if pos.startswith('NN') or pos in ['JJ']:
                # Score based on frequency and POS
                score = tokens.count(token) * (2 if pos.startswith('NN') else 1.5)
                key_phrases.append((token, score))
        
        # Sort by score and remove duplicates
        key_phrases = list(set(key_phrases))
        key_phrases.sort(key=lambda x: x[1], reverse=True)
        
        return key_phrases[:n]
