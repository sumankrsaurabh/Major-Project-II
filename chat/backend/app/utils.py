import io
import re
from collections import Counter
from typing import Dict, List, Tuple

import fitz
import numpy as np
from PIL import Image
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import download, sent_tokenize

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

download("punkt", quiet=True)


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


def extract_key_insights(text: str, max_items: int = 5) -> List[str]:
    words = re.findall(r"\b[a-zA-Z]{5,}\b", text.lower())
    common = Counter(words).most_common(max_items)
    if not common:
        return ["No strong insights were found in this document."]
    return [f"Focus on '{word}' (appears {count} times)" for word, count in common]


def build_graph_data(text: str) -> Dict[str, List]:
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    counter = Counter(words)
    most_common = counter.most_common(8)
    labels = [item[0] for item in most_common]
    values = [item[1] for item in most_common]
    return {"labels": labels, "values": values}


def answer_question_naive(question: str, document_text: str) -> Tuple[str, str]:
    if not document_text.strip():
        return "The document is empty, so I cannot answer questions right now.", "No text available"

    question_terms = set(re.findall(r"\w+", question.lower()))
    sentences = sent_tokenize(document_text)
    scored = []

    for sentence in sentences:
        sentence_terms = set(re.findall(r"\w+", sentence.lower()))
        score = len(question_terms.intersection(sentence_terms))
        if score > 0:
            scored.append((score, sentence))

    if scored:
        scored.sort(reverse=True, key=lambda item: item[0])
        best_sentence = scored[0][1]
        return best_sentence, best_sentence

    summary = summarize_text(document_text, max_sentences=2)
    return (
        f"I could not find a direct answer, but here is a short summary from the document: {summary}",
        "Summary fallback",
    )
