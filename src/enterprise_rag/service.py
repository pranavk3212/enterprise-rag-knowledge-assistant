from ollama import Client

from enterprise_rag.config import CHAT_MODEL, TOP_K
from enterprise_rag.schemas import Answer, Chunk
from enterprise_rag.vector_store import VectorStore


SYSTEM_PROMPT = """You are an internal enterprise knowledge assistant. Answer only using the supplied evidence.
Every factual sentence must end with one or more exact citations in the form [filename · chunk N].
Always conclude with a Sources line that names the evidence chunks you used.
If evidence is insufficient, say: "I don't have enough information in the indexed documents to answer that." Do not use outside knowledge.
Keep the response concise and helpful."""


class EnterpriseRAG:
    def __init__(self) -> None:
        self.store = VectorStore()
        self.client = Client()

    def retrieve(self, question: str, k: int = TOP_K) -> list[Chunk]:
        return self.store.search(question, k)

    def answer(self, question: str) -> Answer:
        sources = self.retrieve(question)
        if not sources:
            return Answer("I don't have any indexed documents yet. Run `rag ingest` first.", [])
        evidence = "\n\n".join(f"[{chunk.label}]\n{chunk.text}" for chunk in sources)
        response = self.client.chat(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Evidence:\n{evidence}\n\nQuestion: {question}"},
            ],
            options={"temperature": 0},
        )
        message = response.message.content if hasattr(response, "message") else response["message"]["content"]
        return Answer(self._with_source_list(message or "No answer generated.", sources), sources)

    @staticmethod
    def _with_source_list(message: str, sources: list[Chunk]) -> str:
        """Provide deterministic source attribution if a small local model omits it."""
        citations = " ".join(f"[{source.label}]" for source in sources)
        return f"{message.rstrip()}\n\nSources: {citations}"
