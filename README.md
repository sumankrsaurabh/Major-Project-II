# ChatWithPDF — Yuktara Technologies

> **Engineering status:** Active modernization. This repository contains an existing prototype and a staged plan toward production readiness. Features described in older sections are not automatically evidence of production readiness; see the engineering roadmap and verify each capability against tests.

## Engineering handbook

- [Target architecture](docs/ARCHITECTURE.md)
- [Engineering roadmap and release gates](docs/ENGINEERING_ROADMAP.md)
- [Contribution and code standards](CONTRIBUTING.md)
- [Product UI standards](docs/PRODUCT_UI_STANDARD.md)
- [Architecture decision records](docs/adr/)

The project is being evolved as a modular monolith with a React client, FastAPI application, replaceable local AI providers, workspace-scoped document indexes, and grounded citations. The current implementation is not yet a production release.

## Current capabilities and limitations

- PDF upload with size and signature validation.
- Browser-local workspace separation and document listing/deletion.
- NumPy-based local vector index using Sentence Transformers embeddings.
- Configurable local Ollama generation, with a clearly labelled extractive fallback.
- Versioned `/api/v1` endpoints; legacy routes remain during migration.
- Automated backend regression tests and frontend lint/build checks.

Important limitations: workspace IDs are not authentication; multi-process storage coordination is not implemented; page-level citations, OCR for scanned PDFs, comprehensive integration tests, and hosted multi-tenant authorization remain outstanding. See the roadmap before deployment.

## 🎯 Quick Navigation

Choose your path based on what you want to do:

### I want to...
- [**Get started quickly**](#quick-start-5-minutes) → 5-minute setup
- [**Understand the features**](#features-overview) → See all 14 features
- [**Learn the API**](#api-quick-reference) → API endpoints
- [**Integrate with my frontend**](#frontend-integration) → React/JavaScript examples
- [**Customize algorithms**](#customization) → Modify behavior
- [**Understand the architecture**](#architecture) → System design

---

## ⚡ Quick Start (5 minutes)

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Start Server
```bash
python -m uvicorn main:app --reload
```

### Step 3: Test It
Open another terminal:
```bash
# Test summarization
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"text":"Your long text...","method":"textrank","num_sentences":3}'

# Test sentiment
curl -X POST http://localhost:8000/sentiment-analysis \
  -H "Content-Type: application/json" \
  -d '{"text":"This is amazing!"}'
```

### Step 4: View API Docs
Visit: http://localhost:8000/docs

---

## ⚙️ Local Development Setup

### Requirements
- Python 3.11
- Node.js 22 and npm
- Ollama (for local generative answers)
- A locally cached Sentence Transformers embedding model

### 1. Configure the backend
```bash
cd backend
python -m venv .venv
# Activate the virtual environment, then:
pip install -r requirements.txt
cp .env.example .env
```

The default configuration uses Ollama with `qwen2.5:3b`. Start Ollama and pull the model:

```bash
ollama pull qwen2.5:3b
```

The embedding model is configured for local-only loading. Download/cache it once in the same Python environment before starting the API:

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

For a non-generative extractive fallback, set `LLM_PROVIDER=extractive` in `.env`. This fallback does not generate new text.

### 2. Start the backend
From the `backend` directory:

```bash
python -m uvicorn main:app --reload
```

### 3. Start the frontend
In a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

### 4. Verify the API
- Health: `http://localhost:8000/api/v1/health`
- OpenAPI docs: `http://localhost:8000/docs`
- Versioned API: `/api/v1`
- Legacy routes remain temporarily available for compatibility.

The application is local-first, but privacy depends on deployment configuration, logs, model settings, and storage access. Do not use this prototype for sensitive or multi-user hosted workloads until the release blockers in the engineering roadmap are closed.

## 📚 Legacy Prototype Feature Inventory

> The following sections document older prototype endpoints and algorithm experiments. They are not a guarantee that every feature is exposed, accurate, or production-supported in the current build. Verify each endpoint and implementation before relying on it.

## 📚 Features Overview

### 1️⃣ Summarization (`/summarize`)
**Compress long text into key points**
```python
{
  "text": "Long document...",
  "method": "textrank",
  "num_sentences": 3
}
```
Returns: Summary, bullet points, compression ratio

---

### 2️⃣ Advanced Q&A (`/advanced-qa`)
**Intelligent question answering with context**
```python
{
  "question": "What is machine learning?",
  "context": "Document content..."
}
```
Returns: Answer, confidence, question type, related questions

---

### 3️⃣ Sentiment Analysis (`/sentiment-analysis`)
**Analyze text emotion and tone**
```python
{
  "text": "This product is amazing!"
}
```
Returns: Sentiment (Positive/Negative/Neutral), confidence score

---

### 4️⃣ Named Entity Recognition (`/named-entity-recognition`)
**Extract important entities (people, places, dates, etc.)**
```python
{
  "text": "Steve Jobs founded Apple in California in 1976."
}
```
Returns: Entities with context and confidence

**Entity Types:**
- PERSON (Steve Jobs)
- ORGANIZATION (Apple)
- LOCATION (California)
- DATE (1976)
- TIME, MONEY, QUANTITY

---

### 5️⃣ Key Phrases (`/extract-keyphrases`)
**Find important phrases in text**
```python
{
  "text": "Your text here...",
  "num_phrases": 5
}
```
Returns: Top phrases with importance scores

---

### 6️⃣ Topics (`/extract-topics`)
**Identify main topics discussed**
```python
{
  "text": "Your text here...",
  "num_topics": 5
}
```
Returns: Main topics with frequency and relevance

---

### 7️⃣ Text Classification (`/classify-text`)
**Categorize text by domain**
```python
{
  "text": "The algorithm processes data..."
}
```
Returns: Category predictions (Technical, Business, Academic, etc.)

---

### 8️⃣ Fact Extraction (`/extract-facts`)
**Find important factual statements**
```python
{
  "text": "Your document..."
}
```
Returns: Factual statements with confidence

---

### 9️⃣ Information Extraction (`/extract-information`)
**Get structured information from text**
```python
{
  "text": "Your document..."
}
```
Returns: Entities, relationships, facts, claims

---

### 🔟 Similarity Check (`/similarity-check`)
**Compare two texts for similarity**
```python
{
  "text1": "Text one...",
  "text2": "Text two..."
}
```
Returns: Similarity scores (Jaccard, Cosine)

---

### 1️⃣1️⃣ Document Comparison (`/compare-documents`)
**Compare two complete documents**
```python
{
  "text1": "Document 1...",
  "text2": "Document 2..."
}
```
Returns: Common elements, unique elements, similarity

---

### 1️⃣2️⃣ Document Analysis (`/document-analysis`)
**Detailed single-document analysis**
```python
{
  "text": "Your document..."
}
```
Returns: Summary, topics, entities, facts, metadata

---

### 1️⃣3️⃣ Semantic Analysis (`/semantic-analysis`)
**Comprehensive text analysis**
```python
{
  "text": "Your text..."
}
```
Returns: Sentiment, topics, keyphrases, categories

---

### 1️⃣4️⃣ Full Analysis (`/full-analysis`)
**Everything combined**
```python
{
  "text": "Your text..."
}
```
Returns: Summarization, semantic analysis, information extraction, metadata

---

## 🔌 API Quick Reference

| Endpoint | Method | Purpose | Input | Output |
|----------|--------|---------|-------|--------|
| `/summarize` | POST | Compress text | text, method | summary, bullets |
| `/advanced-qa` | POST | Answer questions | question, context | answer, confidence |
| `/sentiment-analysis` | POST | Analyze emotion | text | sentiment, score |
| `/named-entity-recognition` | POST | Extract entities | text | entities with context |
| `/extract-keyphrases` | POST | Find key phrases | text | phrases with scores |
| `/extract-topics` | POST | Identify topics | text | topics with frequency |
| `/classify-text` | POST | Categorize text | text | categories with confidence |
| `/extract-facts` | POST | Find facts | text | factual statements |
| `/extract-information` | POST | Structured info | text | entities, facts, relations |
| `/similarity-check` | POST | Compare texts | text1, text2 | similarity scores |
| `/compare-documents` | POST | Compare docs | text1, text2 | comparison results |
| `/document-analysis` | POST | Detailed analysis | text | complete analysis |
| `/semantic-analysis` | POST | Semantic analysis | text | full semantic breakdown |
| `/full-analysis` | POST | Everything | text | all features |

---

## 💻 Frontend Integration

### React Example
```javascript
import React, { useState } from 'react';

function TextAnalyzer() {
  const [text, setText] = useState('');
  const [results, setResults] = useState(null);
  
  const analyzeFull = async () => {
    const response = await fetch('http://localhost:8000/full-analysis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await response.json();
    setResults(data);
  };
  
  return (
    <div>
      <textarea 
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste your text here..."
      />
      <button onClick={analyzeFull}>Analyze</button>
      
      {results && (
        <div>
          <h3>Summary</h3>
          <p>{results.summarization.extractive}</p>
          
          <h3>Sentiment</h3>
          <p>{results.semantic_analysis.sentiment.sentiment}</p>
          
          <h3>Entities</h3>
          <ul>
            {Object.entries(results.information.named_entities).map(([type, entities]) => (
              <li key={type}>{type}: {entities.map(e => e.text).join(', ')}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default TextAnalyzer;
```

### Vue Example
```javascript
// Use same API structure, just with Vue syntax
async function analyzeText(text) {
  const response = await fetch('/full-analysis', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  return await response.json();
}
```

---

## 🛠️ Customization

### Add Custom Sentiment Words
Edit `backend/services/semantic_service.py`:
```python
self.positive_words = {
    'good', 'great', 'excellent', 'awesome',
    # Add your custom words here
    'your_word', 'another_word'
}
```

### Add Custom Entity Patterns
Edit `backend/services/information_extraction_service.py`:
```python
self.patterns = {
    'CUSTOM_ENTITY': [r'your_regex_pattern']
}
```

### Add Custom Categories
Edit `backend/services/semantic_service.py`:
```python
self.categories = {
    'YourCategory': ['keyword1', 'keyword2', ...]
}
```

---

## 📊 Architecture

The system has these layers:

```
FastAPI Server (main.py)
├── Advanced Features Service (Coordinator)
├── Summarization Service
├── Q&A Service
├── Semantic Service
├── Information Extraction Service
└── RAG Service (Original Q&A)
```

Each service uses custom algorithms:
- **TextRank** for summarization
- **TFIDF** for frequency-based analysis
- **PageRank** for importance scoring
- **Regex patterns** for entity recognition
- **Similarity metrics** for comparison
- **Sentiment lexicons** for emotion analysis

---

## 📁 File Structure

```
backend/
├── main.py (API server with 14 endpoints)
├── config.py (Configuration)
├── requirements.txt (Dependencies)
├── core/
│   ├── pdf_processor.py
│   ├── vector_store.py
│   ├── tokenizer.py
│   └── ... (other NLP modules)
├── services/
│   ├── summarization_service.py (NEW)
│   ├── advanced_qa_service.py (NEW)
│   ├── semantic_service.py (NEW)
│   ├── information_extraction_service.py (NEW)
│   ├── advanced_features_service.py (NEW - Coordinator)
│   ├── rag_service.py
│   ├── embedding_service.py
│   └── llm_service.py
├── models/
└── conversations/
```

---

## 🚀 Deployment

### Local Development
```bash
python -m uvicorn main:app --reload
```

### Production with Gunicorn
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Docker
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

---

## 📈 Performance

### Speed Benchmarks
- **Summarization**: ~100ms for 1000 words
- **Sentiment**: ~50ms
- **NER**: ~100ms
- **Full Analysis**: ~500ms

### Memory Usage
- **Minimal** - All algorithms are memory efficient
- **No model loading** - Pure Python algorithms
- **Good for resource-constrained environments**

---

## 🔒 Privacy & Security

✅ **All processing is local**
- ✅ No cloud API calls
- ✅ No data sent outside your server
- ✅ Completely private
- ✅ GDPR compliant
- ✅ Perfect for sensitive documents

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | This file - Overview and quick start |
| `QUICK_START.md` | Detailed setup and examples |
| `API_DOCUMENTATION.md` | Complete API reference |
| `FEATURE_SUMMARY.md` | Feature details and comparisons |
| `ARCHITECTURE.md` | System design and architecture |

---

## ❓ FAQ

**Q: Do I need an API key?**
A: No! Everything runs locally on your server.

**Q: Can I customize the algorithms?**
A: Yes! All code is in Python and easily customizable.

**Q: What about privacy?**
A: Complete privacy - no external APIs or cloud services.

**Q: How fast is it?**
A: Most operations complete in 50-500ms depending on text size.

**Q: Can I use this in production?**
A: Yes! It's designed for production use.

**Q: What about load?**
A: Scales well. Use Uvicorn workers for concurrent requests.

---

## 🎓 Learning Path

1. **Start Here**: Read this README
2. **Quick Setup**: Follow QUICK_START.md
3. **Explore APIs**: Try endpoints in QUICK_START.md
4. **Deep Dive**: Read API_DOCUMENTATION.md
5. **Understand System**: Read ARCHITECTURE.md
6. **Customize**: Edit service files in backend/services/

---

## 🚦 Next Steps

1. **Install** dependencies (`pip install -r requirements.txt`)
2. **Start** server (`python -m uvicorn main:app --reload`)
3. **Test** endpoints (see QUICK_START.md)
4. **Integrate** with frontend (see examples in this file)
5. **Customize** algorithms (edit service files)
6. **Deploy** to production (see DEPLOYMENT section)

---

## 💡 Examples & Use Cases

### PDF Document Analysis
- Upload PDF
- Get summary, entities, topics automatically
- Ask questions about content

### Review Analysis System
- Collect customer reviews
- Analyze sentiment
- Extract key feedback
- Identify trends

### Research Paper Analyzer
- Extract key concepts
- Find relationships
- Compare with other papers
- Generate summaries

### Content Management
- Auto-tag documents
- Suggest categories
- Find duplicates
- Organize by topic

---

## 🤝 Support

For issues or questions:
1. Check documentation files
2. Review API examples in QUICK_START.md
3. Check service source code comments
4. Review error messages and logs

---

## ✨ Summary

You now have a **powerful NLP system** with:
- 14 advanced features
- Custom algorithms
- Fast processing
- Complete privacy
- Easy integration
- Well documented

**Start building amazing AI applications! 🎉**

---

## 📞 Quick Links

- **API Interactive Docs**: http://localhost:8000/docs
- **API JSON Schema**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

---

**Ready to start?**
→ Go to [QUICK_START.md](QUICK_START.md) for setup instructions
→ Go to [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for endpoint details
→ Go to [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
