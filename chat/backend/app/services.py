import base64
from typing import List
from fastapi import UploadFile
from app.schemas import GraphData
from app.utils import (
    extract_text_and_images,
    summarize_text,
    extract_key_insights,
    extract_key_phrases,
    build_graph_data,
    build_section_summaries,
    answer_question_semantic,
)


async def process_pdfs(files: List[UploadFile]):
    documents = []
    for upload in files:
        pdf_bytes = await upload.read()
        text, raw_images = extract_text_and_images(pdf_bytes)
        summary = summarize_text(text)
        insights = extract_key_insights(text)
        graph_payload = build_graph_data(text)
        key_phrases = extract_key_phrases(text)
        sections = build_section_summaries(text)

        images = []
        for item in raw_images:
            encoded = base64.b64encode(item["data"]).decode("utf-8")
            images.append(
                {
                    "name": item["name"],
                    "mime_type": item["mime_type"],
                    "base64": f"data:{item['mime_type']};base64,{encoded}",
                    "width": item.get("width"),
                    "height": item.get("height"),
                    "ocr_text": item.get("ocr_text"),
                }
            )

        documents.append(
            {
                "name": upload.filename or "uploaded.pdf",
                "summary": summary,
                "key_insights": insights,
                "key_phrases": key_phrases,
                "sections": sections,
                "text": text,
                "images": images,
                "graph_data": GraphData(**graph_payload),
            }
        )

    return {"documents": documents}


def answer_question(question: str, document_text: str):
    answer, source = answer_question_semantic(question, document_text)
    return {"answer": answer, "source": source, "context": source}
