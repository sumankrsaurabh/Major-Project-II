# Backend for Chat With Your PDF

This FastAPI backend accepts PDF uploads and returns structured document intelligence.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Features

- Automatic multi-PDF upload processing
- Extract text and images from PDFs
- Semantic question answering with passage retrieval
- Summaries, key phrases, top document sections, and keyword graphs
- OCR support for embedded images

## Endpoints

- `POST /api/upload`: upload single or multiple PDF files
- `POST /api/qa`: ask a question about extracted document text
