import os
import re
import sys
from pathlib import Path
from typing import Any

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types
from sentence_transformers import SentenceTransformer, util


BASE_DIR = Path(__file__).resolve().parents[1]
CHROMA_DIR = BASE_DIR / "data" / "chroma"
COLLECTION_NAME = "enterprise-docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
GEMINI_MODEL = "gemini-3.5-flash-lite"

FALLBACK_ANSWER = (
    "I cannot find this information in the provided documents."
)

load_dotenv(BASE_DIR / ".env")

embedding_model = SentenceTransformer(EMBEDDING_MODEL)


def split_sentences(text: str) -> list[str]:
    """Split document text into searchable sentences."""
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text.strip())

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def retrieve(
    query: str,
    top_k: int = 5,
    max_sentences: int = 10,
) -> list[dict[str, Any]]:
    """Retrieve chunks, then keep only the most relevant sentences."""
    if not query.strip():
        raise ValueError("The query cannot be empty.")

    chroma = chromadb.PersistentClient(path=str(CHROMA_DIR))

    try:
        collection = chroma.get_collection(COLLECTION_NAME)
    except Exception as error:
        raise RuntimeError(
            "ChromaDB collection not found. Run python ingest.py first."
        ) from error

    document_count = collection.count()

    if document_count == 0:
        return []

    query_embedding = embedding_model.encode(
        [query],
        show_progress_bar=False,
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, document_count),
        include=["documents", "metadatas"],
    )

    documents = (results.get("documents") or [[]])[0]
    metadatas = (results.get("metadatas") or [[]])[0]

    candidates = []

    for document, metadata in zip(documents, metadatas):
        if not document:
            continue

        metadata = metadata or {}

        for sentence in split_sentences(document):
            candidates.append(
                {
                    "content": sentence,
                    "source": metadata.get("source", "unknown"),
                    "chunk": metadata.get("chunk", "unknown"),
                }
            )

    if not candidates:
        return []

    sentences = [candidate["content"] for candidate in candidates]

    sentence_embeddings = embedding_model.encode(
        sentences,
        convert_to_tensor=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    query_tensor = embedding_model.encode(
        [query],
        convert_to_tensor=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    similarity_scores = util.cos_sim(
        query_tensor,
        sentence_embeddings,
    )[0]

    ranked_candidates = sorted(
        zip(candidates, similarity_scores.tolist()),
        key=lambda item: item[1],
        reverse=True,
    )

    selected = []
    seen_sentences = set()

    for candidate, _score in ranked_candidates:
        sentence_key = candidate["content"].casefold()

        if sentence_key in seen_sentences:
            continue

        seen_sentences.add(sentence_key)
        selected.append(candidate)

        if len(selected) >= max_sentences:
            break

    return selected


def build_prompt(
    query: str,
    snippets: list[dict[str, Any]],
) -> str:
    """Build a concise, context-grounded Gemini prompt."""
    context_parts = []

    for index, snippet in enumerate(snippets, start=1):
        context_parts.append(
            f"[Source {index}: {snippet['source']}, "
            f"chunk {snippet['chunk']}]\n"
            f"{snippet['content']}"
        )

    context = "\n\n".join(context_parts)

    return f"""
You are Northstar Operations Group's qualitative documentation assistant.

Answer the user's question using ONLY the relevant document excerpts below.

Response requirements:
- Give only the information necessary to answer the question.
- Use a concise paragraph or 2 to 5 bullet points.
- Do not repeat the excerpts word for word.
- Do not summarize unrelated policy areas.
- Do not include a separate "Context" section.
- Do not invent facts, policies, dates, owners, metrics, or procedures.
- Cite factual statements using [Source 1], [Source 2], or multiple sources.
- If the excerpts do not answer the question, respond exactly:
  "I cannot find this information in the provided documents."
- Do not calculate SQL metrics from qualitative text.

RELEVANT DOCUMENT EXCERPTS:
{context}

USER QUESTION:
{query}

CONCISE ANSWER:
""".strip()


def get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY was not found in the project .env file."
        )

    return genai.Client(api_key=api_key)


def get_usage_value(usage: Any, field_name: str) -> int:
    if usage is None:
        return 0

    return int(getattr(usage, field_name, 0) or 0)


def run(query: str) -> dict[str, Any]:
    """Retrieve focused context and generate a concise Gemini answer."""
    snippets = retrieve(
        query=query,
        top_k=5,
        max_sentences=10,
    )

    if not snippets:
        return {
            "answer": FALLBACK_ANSWER,
            "chunks": [],
            "input_tokens": 0,
            "output_tokens": 0,
        }

    prompt = build_prompt(query, snippets)
    gemini = get_gemini_client()

    response = gemini.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=500,
        ),
    )

    answer = (response.text or "").strip() or FALLBACK_ANSWER
    usage = getattr(response, "usage_metadata", None)

    return {
        "answer": answer,
        "chunks": snippets,
        "input_tokens": get_usage_value(
            usage,
            "prompt_token_count",
        ),
        "output_tokens": get_usage_value(
            usage,
            "candidates_token_count",
        ),
    }


def main() -> None:
    query = " ".join(sys.argv[1:]).strip()

    if not query:
        query = input("Enter your question: ").strip()

    result = run(query)
    print(result["answer"])


if __name__ == "__main__":
    main()
