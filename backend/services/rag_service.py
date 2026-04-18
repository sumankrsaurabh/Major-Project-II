import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from core.vector_store import load_vector_store
from services.llm_service import get_llm
from config import TOP_K

logger = logging.getLogger(__name__)


def generate_answer(query: str):
    """Synchronous answer generation"""
    store = load_vector_store()

    if not store:
        return {
            "answer": "No document uploaded."
        }

    docs = store.similarity_search(query, k=TOP_K)

    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
You are an AI assistant.

Answer ONLY using the provided context.

Context:
{context}

Question: {query}

Answer:
"""

    llm = get_llm()

    response = llm.invoke(prompt)

    return {
        "answer": response.content
    }


async def generate_answer_async(query: str):
    """
    Asynchronous answer generation
    Runs vector search and LLM in thread pool
    """
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=4)
    
    try:
        # Run the synchronous generate_answer in thread pool
        result = await loop.run_in_executor(
            executor,
            generate_answer,
            query
        )
        return result
    except Exception as e:
        logger.error(f"Answer generation error: {e}")
        return {
            "answer": f"Error generating answer: {str(e)}",
            "sources": []
        }
