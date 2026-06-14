# Architecture & System Design

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Server                             │
│                     (main.py)                                   │
└─────────────────────────────────────────────────────────────────┘
         │
         ├── PDF Upload & Processing
         │   ├── pdf_processor.py (PDF text extraction)
         │   └── vector_store.py (Vector embeddings)
         │
         ├── Core AI/ML/NLP/CV Modules (backend/core/)
         │   ├── nlp_processor.py (NLP pipeline)
         │   ├── computer_vision.py (OCR & image processing)
         │   ├── machine_learning.py (ML models)
         │   ├── ai_engine.py (AI reasoning)
         │   ├── pdf_processor.py (PDF processing)
         │   └── vector_store.py (Vector storage)
         │
         ├── Integration Services (backend/services/)
         │   ├── comprehensive_analysis_service.py (Main integration)
         │   ├── rag_service.py (RAG Q&A)
         │   ├── embedding_service.py (Embeddings)
         │   ├── llm_service.py (Language model)
         │   └── __init__.py (Module init)
         │
         ├── API Routes (backend/routes/)
         │   ├── analysis_routes.py (8+ analysis endpoints)
         │   └── __init__.py (Route init)
         │
         └── API Endpoints
             ├── /upload (PDF upload)
             ├── /chat (Q&A)
             ├── /clear-conversation (Clear history)
             ├── /status (System status)
             └── /api/analysis/* (15+ advanced endpoints)
```

## Clean Architecture

---

## Request/Response Flow

### Example: Summarization Request
```
User Request
    ↓
REST API (/summarize)
    ↓
AdvancedFeaturesService
    ↓
AdvancedSummarizationService
    ├── TextRankSummarizer
    │   ├── Sentence tokenization
    │   ├── Word tokenization
    │   ├── Similarity matrix calculation
    │   ├── PageRank score calculation
    │   └── Top sentence selection
    └── FrequencyBasedSummarizer
        ├── Sentence tokenization
        ├── Word tokenization & filtering
        ├── TFIDF score calculation
        └── Top sentence selection
    ↓
Response with Summary
    ↓
Client (Web/Mobile/Python)
```

### Example: NER Request
```
User Request
    ↓
REST API (/named-entity-recognition)
    ↓
InformationExtractor
    ↓
NamedEntityRecognizer
    ├── Regex Pattern Matching
    │   ├── DATE patterns
    │   ├── TIME patterns
    │   ├── MONEY patterns
    │   ├── QUANTITY patterns
    │   ├── PERSON patterns
    │   ├── LOCATION patterns
    │   └── ORGANIZATION patterns
    ├── Entity Extraction
    ├── Context Addition
    └── Confidence Scoring
    ↓
Response with Entities
    ↓
Client
```

---

## Module Dependencies

```
main.py (FastAPI Server)
    ├── comprehensive_analysis_service.py (Integration Layer)
    │   ├── nlp_processor.py (NLP pipeline)
    │   │   ├── AdvancedTokenizer
    │   │   ├── Lemmatizer
    │   │   ├── POSTagger
    │   │   ├── NamedEntityRecognizer
    │   │   ├── DependencyParser
    │   │   └── SyntacticAnalyzer
    │   │
    │   ├── computer_vision.py (CV module)
    │   │   ├── OCRProcessor
    │   │   ├── ImageProcessor
    │   │   └── DocumentAnalyzer
    │   │
    │   ├── machine_learning.py (ML models)
    │   │   ├── TextClassifier
    │   │   ├── DocumentClustering
    │   │   ├── AnomalyDetector
    │   │   └── RecommendationEngine
    │   │
    │   └── ai_engine.py (AI reasoning)
    │       ├── IntentRecognizer
    │       ├── DialogueManager
    │       ├── KnowledgeGraph
    │       ├── ReasoningEngine
    │       └── QuestionAnalyzer
    │
    ├── rag_service.py (RAG Q&A)
    │   ├── vector_store.py
    │   ├── embedding_service.py
    │   └── llm_service.py
    │
    ├── routes/analysis_routes.py (API endpoints)
    │   └── comprehensive_analysis_service
    │
    ├── pdf_processor.py (PDF extraction)
    │   └── pdfplumber
    │
    └── Other modules (config, models, etc.)
```

---

## Data Flow Architecture

### 1. PDF Upload & Processing
```
PDF File
    ↓
pdfplumber.open()
    ↓
Text Extraction
    ↓
SimpleTokenizer
    ├── Sentence splitting
    └── Chunk creation
    ↓
Chunk Embeddings (embedding_service)
    ↓
Vector Store (FAISS)
    ↓
Ready for Q&A
```

### 2. Chat/Q&A Processing
```
User Question
    ↓
Vector Embedding
    ↓
FAISS Similarity Search
    ↓
Retrieved Relevant Chunks
    ↓
LLM Context Creation
    ↓
LLM Response Generation
    ↓
Conversation History Update
    ↓
Response to User
```

### 3. Advanced Analysis Processing
```
Input Text
    ├─ Summarization
    │   ├── Tokenization
    │   ├── Algorithm Selection
    │   └── Summary Generation
    │
    ├─ Semantic Analysis
    │   ├── Tokenization
    │   ├── Sentiment Analysis
    │   ├── Topic Extraction
    │   ├── Phrase Extraction
    │   └── Classification
    │
    ├─ Information Extraction
    │   ├── Named Entity Recognition
    │   ├── Relationship Extraction
    │   └── Fact Extraction
    │
    └─ Similarity Calculation
        ├── Token Generation
        ├── Similarity Metrics
        └── Score Calculation
         ↓
    Consolidated Results
         ↓
    User Response
```

---

## Class Hierarchy

```
AdvancedFeaturesService
├── AdvancedSummarizationService
│   ├── TextRankSummarizer
│   └── FrequencyBasedSummarizer
│
├── AdvancedQAService
│   ├── QuestionTypeClassifier
│   ├── AnswerExtractor
│   └── SemanticAnswerMatcher
│
├── AdvancedSemanticService
│   ├── SentimentAnalyzer
│   ├── KeyPhraseExtractor
│   ├── TopicExtractor
│   ├── TextClassifier
│   └── SemanticSimilarityCalculator
│
└── InformationExtractor
    ├── NamedEntityRecognizer
    ├── RelationshipExtractor
    └── FactExtractor
```

---

## API Endpoint Grouping

### Text Analysis Endpoints
- `/summarize` - Extractive summarization
- `/semantic-analysis` - Full semantic analysis
- `/classify-text` - Text categorization
- `/extract-topics` - Topic identification

### Entity & Information Endpoints
- `/named-entity-recognition` - Entity extraction
- `/extract-information` - Structured information
- `/extract-facts` - Fact extraction
- `/extract-keyphrases` - Key phrase extraction

### Question & Answer Endpoints
- `/chat` - PDF Q&A (Original)
- `/advanced-qa` - Advanced Q&A

### Comparison & Similarity Endpoints
- `/similarity-check` - Text similarity
- `/compare-documents` - Document comparison

### Sentiment Endpoints
- `/sentiment-analysis` - Sentiment analysis

### Comprehensive Endpoints
- `/document-analysis` - Detailed analysis
- `/full-analysis` - Complete analysis

---

## Algorithm Complexity & Performance

### Summarization
| Algorithm | Time Complexity | Space | Speed |
|-----------|-----------------|-------|-------|
| TextRank | O(n log n) | O(n²) | ~100ms |
| Frequency | O(n) | O(n) | ~50ms |

### NER
| Task | Time Complexity | Speed |
|------|-----------------|-------|
| Pattern Matching | O(n*m) | ~100ms |
| Entity Grouping | O(n log n) | ~20ms |

### Sentiment
| Task | Time Complexity | Speed |
|------|-----------------|-------|
| Tokenization | O(n) | ~20ms |
| Scoring | O(n) | ~30ms |

### Similarity
| Method | Complexity | Speed |
|--------|-----------|-------|
| Jaccard | O(n+m) | ~50ms |
| Cosine | O(n*m) | ~80ms |

---

## Configuration Files

### config.py
```python
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
CHUNK_SIZE = 1000  # tokens per chunk
CHUNK_OVERLAP = 200  # overlap between chunks
TOP_K = 3  # retrieval results
TEMPERATURE = 0.7  # LLM temperature
MAX_HISTORY = 10  # conversation history
SIMILARITY_THRESHOLD = 0.7
RERANKING_ENABLED = True
CONVERSATION_ENABLED = True
```

---

## Environment Setup

### Requirements.txt Structure
```
Core Dependencies
├── FastAPI/Uvicorn (Server)
├── pdfplumber (PDF processing)
└── python-dotenv (Configuration)

NLP Libraries
├── nltk (Natural Language Toolkit)
├── spacy (Industrial NLP)
├── gensim (Topic modeling)
└── scikit-learn (ML utilities)

Data Processing
├── pandas (Data manipulation)
├── numpy (Numerical computing)
├── scipy (Scientific computing)
└── regex (Pattern matching)

Advanced Features
├── transformers (Deep learning)
├── torch (PyTorch)
├── rouge-score (Summary evaluation)
└── rank-bm25 (Ranking)
```

---

## Concurrent Request Handling

```
Request 1 (Summarize)  ──┐
Request 2 (Q&A)        ──├──> Uvicorn (async)
Request 3 (Sentiment)  ──┤    ThreadPoolExecutor
Request 4 (NER)        ──┘    (Each service)
                              │
                              ├── CPU bound: ~4 threads
                              └── IO bound: ~2 threads
                                  │
                                  ↓
                              Responses
```

---

## Memory Management

### Vector Storage
```
FAISS Index
├── Document embeddings (vectors.npy)
├── Metadata (documents.json)
└── Search index (index.faiss)
```

### Conversation Storage
```
backend/conversations/
├── session_1.json
├── session_2.json
└── ...
```

### Cache Strategy
```
In-Memory Cache
├── Model weights
├── Vectorizer
└── Conversation history (LRU)
```

---

## Scalability Considerations

### For Higher Load:
1. **Load Balancing** - Use Nginx/HAProxy
2. **Async Workers** - Increase Uvicorn workers
3. **Caching** - Add Redis for caching
4. **Database** - Store results in PostgreSQL
5. **Queue System** - Use Celery for async tasks
6. **Monitoring** - Add Prometheus metrics

### For Better Performance:
1. **GPU Support** - Add CUDA for vectorization
2. **Model Optimization** - Use quantization
3. **Batch Processing** - Process multiple texts
4. **Indexing** - Optimize search indices
5. **Compression** - Compress stored vectors

---

## Security Considerations

✅ **Implemented:**
- CORS support for frontend
- Input validation
- File size limits
- Error handling
- Logging

**To Add:**
- Authentication (JWT)
- Rate limiting
- API keys
- HTTPS
- Request encryption

---

## Testing Strategy

```
Unit Tests
├── Service functions
├── Algorithm correctness
└── Edge cases

Integration Tests
├── API endpoints
├── Service coordination
└── End-to-end flows

Performance Tests
├── Speed benchmarks
├── Memory usage
└── Scalability limits

Load Tests
├── Concurrent requests
├── Large file handling
└── Extended usage
```

---

## Deployment Architecture

```
Development
└── Local machine with hot reload

Production (Minimal)
├── Uvicorn server
├── Nginx reverse proxy
└── File storage

Production (Scalable)
├── Docker containers
├── Kubernetes orchestration
├── Redis cache
├── PostgreSQL database
├── S3 object storage
└── Monitoring stack
```

---

## Technology Stack Summary

| Layer | Technology |
|-------|-----------|
| API Framework | FastAPI |
| Server | Uvicorn |
| NLP Core | Custom Python |
| ML Libraries | scikit-learn, numpy |
| Text Processing | nltk, spacy, regex |
| Data Storage | FAISS, JSON files |
| Vector DB | FAISS (in-memory) |
| Frontend | React (separate) |
| Database | File-based (optional PostgreSQL) |
| Caching | In-memory (optional Redis) |

---

## Development Workflow

```
1. Feature Request
    ↓
2. Create Service Class
    ├── Algorithm implementation
    ├── Error handling
    └── Documentation
    ↓
3. Add FastAPI Endpoint
    ├── Request validation
    ├── Service integration
    └── Response formatting
    ↓
4. Test Locally
    ├── Unit tests
    ├── Manual testing
    └── Performance check
    ↓
5. Document
    ├── API docs
    ├── Examples
    └── Use cases
```

This architecture is designed to be:
- **Scalable** - Easy to add new features
- **Maintainable** - Clear separation of concerns
- **Performant** - Optimized algorithms
- **Extensible** - Simple to customize
- **Secure** - Built-in safety measures
