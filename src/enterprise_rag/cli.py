import argparse
import json

from enterprise_rag.config import CHUNK_OVERLAP, CHUNK_SIZE, DOCUMENTS_DIR, EVALUATION_FILE, TOP_K
from enterprise_rag.loaders import SUPPORTED_SUFFIXES, read_document, recursive_chunks
from enterprise_rag.schemas import Chunk
from enterprise_rag.service import EnterpriseRAG
from enterprise_rag.vector_store import VectorStore


def _has_inline_expected_source_citation(answer: str, expected_source: str) -> bool:
    """Check the answer body for the expected source, excluding the auto-added Sources footer.

    This is a citation-presence proxy only; it does not verify that the cited passage
    semantically supports the answer.
    """
    answer_body = answer.split("\n\nSources:", maxsplit=1)[0]
    return f"[{expected_source} · chunk " in answer_body


def ingest() -> None:
    if not DOCUMENTS_DIR.exists():
        raise FileNotFoundError(f"Document folder does not exist: {DOCUMENTS_DIR}")
    chunks: list[Chunk] = []
    documents = [path for path in DOCUMENTS_DIR.rglob("*") if path.suffix.lower() in SUPPORTED_SUFFIXES]
    for path in documents:
        source = path.relative_to(DOCUMENTS_DIR).as_posix()
        for number, text in enumerate(recursive_chunks(read_document(path), CHUNK_SIZE, CHUNK_OVERLAP), start=1):
            chunks.append(Chunk(id=f"{source}:{number}", text=text, source=source, chunk_number=number))
    if not chunks:
        raise ValueError("No supported documents found. Add .md, .txt, or .pdf files to data/documents.")
    store = VectorStore()
    store.reset()
    count = store.upsert(chunks)
    print(f"Indexed {count} chunks from {len(documents)} documents.")


def evaluate() -> None:
    cases = json.loads(EVALUATION_FILE.read_text(encoding="utf-8"))
    assistant = EnterpriseRAG()
    retrieval_hits = 0
    citation_hits = 0
    print(f"Evaluating {len(cases)} questions...\n")
    for case in cases:
        sources = assistant.retrieve(case["question"])
        retrieved_names = {source.source for source in sources}
        retrieval_hit = case["expected_source"] in retrieved_names
        result = assistant.answer(case["question"])
        citation_hit = _has_inline_expected_source_citation(result.answer, case["expected_source"])
        retrieval_hits += retrieval_hit
        citation_hits += citation_hit
        print(
            f"{'PASS' if retrieval_hit else 'MISS'} retrieval | "
            f"{'PASS' if citation_hit else 'MISS'} inline citation proxy | {case['question']}"
        )
    total = len(cases)
    print(f"\nTop-{TOP_K} retrieval hit rate: {retrieval_hits / total:.1%}")
    print(f"Inline expected-source citation proxy: {citation_hits / total:.1%}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Enterprise RAG assistant")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("ingest", help="Index files in data/documents")
    ask_parser = subparsers.add_parser("ask", help="Ask a question")
    ask_parser.add_argument("question")
    subparsers.add_parser("evaluate", help="Run the evaluation set")
    args = parser.parse_args()
    if args.command == "ingest":
        ingest()
    elif args.command == "ask":
        print(EnterpriseRAG().answer(args.question).answer)
    else:
        evaluate()


if __name__ == "__main__":
    main()
