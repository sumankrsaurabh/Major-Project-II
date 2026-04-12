import io
import re
from collections import Counter
from typing import Dict, List, Tuple

import fitz
import numpy as np
from PIL import Image
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from nltk import download, sent_tokenize

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    TRANSFORMERS_AVAILABLE = False


download("punkt", quiet=True)
EMBEDDING_MODEL = None


def get_embedding_model():
    global EMBEDDING_MODEL
    if EMBEDDING_MODEL is None and TRANSFORMERS_AVAILABLE:
        EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return EMBEDDING_MODEL


def extract_text_and_images(pdf_bytes: bytes) -> Tuple[str, List[Dict]]:
    document = fitz.open(stream=pdf_bytes, filetype="pdf")
    all_text = []
    image_items = []

    for page_index, page in enumerate(document, start=1):
        all_text.append(page.get_text())

        for img_index, img in enumerate(page.get_images(full=True), start=1):
            xref = img[0]
            base_image = document.extract_image(xref)
            image_bytes = base_image["image"]
            mime_type = base_image.get("ext", "png")
            image_name = f"page_{page_index}_img_{img_index}.{mime_type}"

            width = None
            height = None
            ocr_text = None

            try:
                picture = Image.open(io.BytesIO(image_bytes))
                width, height = picture.size
                if TESSERACT_AVAILABLE:
                    try:
                        ocr_text = pytesseract.image_to_string(picture)
                    except Exception:
                        ocr_text = None
            except Exception:
                pass

            image_items.append(
                {
                    "name": image_name,
                    "mime_type": f"image/{mime_type}",
                    "data": image_bytes,
                    "width": width,
                    "height": height,
                    "ocr_text": ocr_text,
                }
            )

    return "\n".join(all_text), image_items


def summarize_text(text: str, max_sentences: int = 3) -> str:
    if not text or len(text.strip()) < 50:
        return text.strip() or "No text content found in the PDF document."

    sentences = sent_tokenize(text)
    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(sentences)
        sentence_scores = matrix.sum(axis=1).A1
        ranked = sorted(enumerate(sentence_scores), key=lambda pair: pair[1], reverse=True)
        top_indices = sorted([idx for idx, _ in ranked[:max_sentences]])
        return " ".join([sentences[index] for index in top_indices])
    except Exception:
        return " ".join(sentences[:max_sentences])


def split_text_into_chunks(text: str, chunk_size: int = 180, overlap: int = 40) -> List[str]:
    if not text.strip():
        return []

    words = re.findall(r"\S+", text)
    if len(words) <= chunk_size:
        return [" ".join(words).strip()]

    chunks = []
    step = max(chunk_size - overlap, 30)
    for start in range(0, len(words), step):
        chunk = words[start : start + chunk_size]
        if chunk:
            chunks.append(" ".join(chunk).strip())
    return chunks


def compute_embeddings(items: List[str], vectorizer=None) -> tuple[np.ndarray, object]:
    if not items:
        return np.empty((0, 0), dtype=float), vectorizer

    if TRANSFORMERS_AVAILABLE:
        model = get_embedding_model()
        try:
            embeddings = model.encode(items, convert_to_numpy=True, normalize_embeddings=True)
            return np.array(embeddings, dtype=float), None
        except Exception:
            pass

    if vectorizer is None:
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(items)
    else:
        if not hasattr(vectorizer, "vocabulary_"):
            matrix = vectorizer.fit_transform(items)
        else:
            matrix = vectorizer.transform(items)

    array = matrix.toarray().astype(float)
    norms = np.linalg.norm(array, axis=1, keepdims=True)
    return array / np.maximum(norms, 1e-9), vectorizer


def cosine_similarity(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    if matrix.size == 0 or query_vec.size == 0:
        return np.array([])

    query_norm = np.linalg.norm(query_vec)
    matrix_norms = np.linalg.norm(matrix, axis=1)
    denom = np.maximum(matrix_norms * query_norm, 1e-9)
    return np.dot(matrix, query_vec) / denom


def semantic_search(question: str, chunks: List[str], top_k: int = 4) -> List[Dict[str, float]]:
    if not chunks:
        return []

    if TRANSFORMERS_AVAILABLE:
        chunk_embeddings, _ = compute_embeddings(chunks)
        question_embedding, _ = compute_embeddings([question])
    else:
        vectorizer = TfidfVectorizer(stop_words="english")
        chunk_embeddings, vectorizer = compute_embeddings(chunks, vectorizer=vectorizer)
        question_embedding, _ = compute_embeddings([question], vectorizer=vectorizer)

    if question_embedding.size == 0 or chunk_embeddings.size == 0:
        return []

    similarities = cosine_similarity(question_embedding[0], chunk_embeddings)
    ranked = sorted(enumerate(similarities), key=lambda pair: pair[1], reverse=True)
    return [
        {"text": chunks[idx], "score": float(score)}
        for idx, score in ranked[: min(top_k, len(ranked))]
    ]


def extract_key_insights(text: str, max_items: int = 5) -> List[str]:
    words = re.findall(r"\b[a-zA-Z]{5,}\b", text.lower())
    filtered = [word for word in words if word not in ENGLISH_STOP_WORDS]
    common = Counter(filtered).most_common(max_items)
    if not common:
        return ["No strong insights were found in this document."]
    return [f"Focus on '{word}' (appears {count} times)" for word, count in common]


def extract_key_phrases(text: str, max_items: int = 6) -> List[str]:
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    filtered = [word for word in words if word not in ENGLISH_STOP_WORDS]
    most_common = Counter(filtered).most_common(max_items)
    return [word for word, _ in most_common] if most_common else ["General document keywords"]


def build_graph_data(text: str) -> Dict[str, List]:
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    filtered = [word for word in words if word not in ENGLISH_STOP_WORDS]
    counter = Counter(filtered)
    most_common = counter.most_common(8)
    labels = [item[0] for item in most_common]
    values = [item[1] for item in most_common]
    return {"labels": labels, "values": values}


def build_section_summaries(text: str, max_sections: int = 5) -> List[Dict[str, float]]:
    chunks = split_text_into_chunks(text, chunk_size=180, overlap=50)
    if not chunks:
        return []

    document_summary = summarize_text(text, max_sentences=3)
    matches = semantic_search(document_summary, chunks, top_k=max_sections)
    sections = []
    for index, match in enumerate(matches):
        preview = " ".join(match["text"].split()[:32])
        if len(match["text"].split()) > 32:
            preview += "..."
        sections.append(
            {
                "title": f"Section {index + 1}",
                "preview": preview,
                "relevance": round(match["score"], 3),
            }
        )
    return sections


def select_best_sentence(question: str, sentences: List[str]) -> str:
    question_terms = set(re.findall(r"\w+", question.lower()))
    best_sentence = ""
    best_score = 0

    for sentence in sentences:
        sentence_terms = set(re.findall(r"\w+", sentence.lower()))
        score = len(question_terms.intersection(sentence_terms))
        if score > best_score:
            best_score = score
            best_sentence = sentence

    return best_sentence or (sentences[0] if sentences else "No matching answer found.")


def answer_question_semantic(question: str, document_text: str) -> Tuple[str, str]:
    if not document_text.strip():
        return "The document is empty, so I cannot answer questions right now.", "No text available"

    chunks = split_text_into_chunks(document_text, chunk_size=180, overlap=50)
    search_results = semantic_search(question, chunks, top_k=4)
    if not search_results:
        fallback = summarize_text(document_text, max_sentences=3)
        return (
            f"I could not locate a precise answer. Here is a related summary: {fallback}",
            "Fallback summary",
        )

    combined_text = " ".join([result["text"] for result in search_results])
    candidate_sentences = sent_tokenize(combined_text)
    answer = select_best_sentence(question, candidate_sentences)
    if not answer:
        answer = search_results[0]["text"]

    source_text = search_results[0]["text"].strip()
    preview_source = source_text[:240] + ("..." if len(source_text) > 240 else "")
    context = "\n\n".join([
        f"[{idx + 1}] {result['text'][:260].strip()}{'...' if len(result['text']) > 260 else ''}"
        for idx, result in enumerate(search_results)
    ])
    return answer, f"{preview_source}\n\n{context}"
