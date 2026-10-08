from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "data" / "chroma"
COLLECTION_NAME = "enterprise-docs"
MODEL_NAME = "all-MiniLM-L6-v2"


def find_documents_folder() -> Path:
    possible_folders = [
        BASE_DIR / "data" / "documents",
        BASE_DIR / "documents",
        BASE_DIR / "data",
    ]

    for folder in possible_folders:
        if folder.is_dir() and list(folder.glob("*.txt")):
            return folder

    raise FileNotFoundError(
        "No folder containing .txt documents was found."
    )


def chunk_document(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    words = text.split()
    step = chunk_size - overlap
    chunks = []

    for index in range(0, len(words), step):
        chunk = " ".join(words[index:index + chunk_size])

        if chunk:
            chunks.append(chunk)

    return chunks


def ingest() -> None:
    documents_folder = find_documents_folder()

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(COLLECTION_NAME)
    model = SentenceTransformer(MODEL_NAME)

    for existing_id in collection.get().get("ids", []):
        collection.delete(ids=[existing_id])

    document_files = sorted(documents_folder.glob("*.txt"))

    for document_path in document_files:
        filename = document_path.name
        text = document_path.read_text(encoding="utf-8")
        chunks = chunk_document(text)

        embeddings = model.encode(
            chunks,
            show_progress_bar=False,
        ).tolist()

        ids = [
            f"{filename}-{index}"
            for index in range(len(chunks))
        ]

        metadatas = [
            {
                "source": filename,
                "chunk": index,
            }
            for index in range(len(chunks))
        ]

        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas,
        )

        print(f"Ingested {len(chunks)} chunks from {filename}")


if __name__ == "__main__":
    ingest()
