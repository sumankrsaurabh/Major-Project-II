# Chat With Your PDF

A full-stack app built with FastAPI, React, and Python tools for PDF summarization, knowledge extraction, question answering, image extraction, and graph analysis.

## Features
- Upload one or multiple PDF files at once
- Extract text and images from PDFs
- Generate document summaries and key insights
- Ask document-specific questions using semantic search
- Extract OCR text from images inside PDFs
- Produce keyword graph data for knowledge exploration
- See top document sections, key phrases, and evidence context

## Getting Started

### Backend

```bash
cd "c:\Users\suman\Code\Major Project II\chat\backend"
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd "c:\Users\suman\Code\Major Project II\chat\frontend"
npm install
npm run dev
```

Then open the Vite app at `http://localhost:5173`.

## Notes
- OCR support uses `pytesseract` if it is installed and configured on your system.
- The project uses lightweight NLP and ML utilities for summarization, keyword extraction, and question matching.
