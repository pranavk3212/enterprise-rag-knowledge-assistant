from collections.abc import Iterable

import chromadb
from ollama import Client

from enterprise_rag.config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
)
from enterprise_rag.schemas import Chunk


class VectorStore:
    def __init__(self) -> None:
        self.client = Client()
        self.db = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.db.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def reset(self) -> None:
        # Deleting the collection avoids file-lock problems from removing the
        # persistence directory while Chroma is active (especially on Windows).
        try:
            self.db.delete_collection(COLLECTION_NAME)
        except ValueError:
            pass
        self.collection = self.db.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embed(model=EMBEDDING_MODEL, input=texts)
        return response.embeddings if hasattr(response, "embeddings") else response["embeddings"]

    def upsert(self, chunks: Iterable[Chunk]) -> int:
        items = list(chunks)
        if not items:
            return 0
        embeddings = self.embed([chunk.text for chunk in items])
        self.collection.upsert(
            ids=[chunk.id for chunk in items],
            documents=[chunk.text for chunk in items],
            embeddings=embeddings,
            metadatas=[{"source": chunk.source, "chunk_number": chunk.chunk_number} for chunk in items],
        )
        return len(items)

    def search(self, query: str, k: int) -> list[Chunk]:
        response = self.collection.query(
            query_embeddings=[self.embed([query])[0]],
            n_results=k,
            include=["documents", "metadatas"],
        )
        documents = response["documents"][0]
        metadata = response["metadatas"][0]
        return [
            Chunk(
                id=f"{item['source']}:{item['chunk_number']}",
                text=text,
                source=item["source"],
                chunk_number=int(item["chunk_number"]),
            )
            for text, item in zip(documents, metadata)
        ]
