import os
import logging
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from config import *

logger = logging.getLogger(__name__)

def get_llm():
    if os.getenv("GROQ_API_KEY"):
        try:
            return ChatGroq(
                model=GROQ_MODEL,
                groq_api_key=os.getenv("GROQ_API_KEY"),
                temperature=0.2
            )
        except Exception as e:
            logger.warning(f"Groq failed: {e}")

    if os.getenv("GOOGLE_API_KEY"):
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.2
        )

    raise Exception("No working LLM available")