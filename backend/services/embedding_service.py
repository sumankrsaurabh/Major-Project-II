from langchain_huggingface import HuggingFaceEmbeddings

_model = None

def get_embedding_model():
    global _model
    if not _model:
        _model = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
    return _model