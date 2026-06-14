import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.tokenizer import SimpleTokenizer
from services.embedding_service import get_embedding_model
from core.vector_store import create_vector_store, load_vector_store
from services.llm_service import get_llm
from services.rag_service import generate_answer

async def run_test():
    print("Starting Pipeline Test...")
    
    # 1. Test Tokenizer
    print("\n[1] Testing Tokenizer...")
    tokenizer = SimpleTokenizer()
    sample_text = "This is a test document. It contains multiple sentences! We will use this to test our custom tokenizer."
    chunks = tokenizer.chunk_text(sample_text, chunk_size=20, chunk_overlap=5)
    print(f"    Created {len(chunks)} chunks.")
    for i, c in enumerate(chunks):
        print(f"    Chunk {i+1}: '{c}'")
        
    # 2. Test Embeddings & Vector Store
    print("\n[2] Testing Embeddings & Vector Store...")
    try:
        # Pass strings directly
        vector_store = create_vector_store(chunks)
        print("    Vector store created and saved successfully.")
        
        # Test similarity search
        print("    Searching for 'test document'...")
        results = vector_store.similarity_search("test document", k=2)
        print(f"    Found {len(results)} results.")
        for r in results:
            print(f"    Result (Score: {r.metadata.get('score', 0):.4f}): {r.page_content}")
    except Exception as e:
        print(f"    Error in Vector Store: {e}")
        return
        
    # 3. Test LLM Generation
    print("\n[3] Testing LLM Context Generation...")
    try:
        answer_data = generate_answer("What is this document about?", session_id="test_session")
        print("    LLM Output:")
        print(f"    Status: {answer_data.get('status')}")
        print(f"    Answer: {answer_data.get('answer')}")
    except Exception as e:
        print(f"    Error in LLM Generation: {e}")
        return
        
    print("\nAll Tests Passed Successfully!")

if __name__ == "__main__":
    asyncio.run(run_test())
