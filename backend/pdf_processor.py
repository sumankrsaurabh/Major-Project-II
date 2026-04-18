from PyPDF2 import PdfReader
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts all text from a given PDF file.
    Handles errors gracefully and returns empty string on failure.
    """
    text = ""
    try:
        reader = PdfReader(file_path)
        
        # Log PDF info
        num_pages = len(reader.pages)
        logger.info(f"PDF has {num_pages} pages")
        
        for page_num, page in enumerate(reader.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num} ---\n{page_text}"
            except Exception as e:
                logger.warning(f"Error extracting page {page_num}: {e}")
                continue
        
        logger.info(f"Extracted {len(text)} characters from PDF")
        return text
        
    except Exception as e:
        logger.error(f"Error reading PDF: {e}", exc_info=True)
        return ""

def get_text_chunks(text: str, chunk_size: int = 1200, chunk_overlap: int = 300) -> list[str]:
    """
    Splits text into overlapping chunks for embeddings.
    Optimized for fast processing while maintaining quality.
    
    Args:
        text: Input text to split
        chunk_size: Size of each chunk (1200 chars - optimal for all-MiniLM model)
        chunk_overlap: Overlap between chunks (300 = 25% for better speed)
    
    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]  # Hierarchical splitting
    )
    
    try:
        chunks = text_splitter.split_text(text)
        # Filter out very small chunks
        chunks = [c for c in chunks if len(c.strip()) > 10]
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    except Exception as e:
        logger.error(f"Error splitting text: {e}")
        return []
