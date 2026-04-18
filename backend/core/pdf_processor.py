import pdfplumber
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

def extract_text(file_path: str) -> str:
    """Synchronous PDF text extraction"""
    text_parts = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                content = page.extract_text()
                if content:
                    text_parts.append(f"\n--- Page {i+1} ---\n{content}")

        return "".join(text_parts)

    except Exception as e:
        logger.error(f"PDF error: {e}")
        return ""


async def extract_text_async(file_path: str) -> str:
    """
    Asynchronous PDF text extraction
    Runs in thread pool to avoid blocking
    """
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=2)
    
    try:
        text = await loop.run_in_executor(
            executor,
            extract_text,
            file_path
        )
        return text
    except Exception as e:
        logger.error(f"Async PDF error: {e}")
        raise

    