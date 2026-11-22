import asyncio
import logging

import pdfplumber

logger = logging.getLogger(__name__)


def extract_pages(file_path: str) -> list[dict]:
    """Extract non-empty page text while preserving one-based PDF page numbers."""
    pages = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                content = (page.extract_text() or "").strip()
                if content:
                    pages.append({"page_number": page_number, "text": content})
        return pages
    except Exception:
        logger.exception("PDF page extraction failed")
        raise


def extract_text(file_path: str) -> str:
    """Backward-compatible text extraction with explicit page separators."""
    return "".join(
        f"\n--- Page {page['page_number']} ---\n{page['text']}"
        for page in extract_pages(file_path)
    )


async def extract_pages_async(file_path: str) -> list[dict]:
    """Run PDF parsing off the event loop without creating per-request executors."""
    return await asyncio.to_thread(extract_pages, file_path)


async def extract_text_async(file_path: str) -> str:
    """Backward-compatible asynchronous text extraction."""
    return await asyncio.to_thread(extract_text, file_path)
