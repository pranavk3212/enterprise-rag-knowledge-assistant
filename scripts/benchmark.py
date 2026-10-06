from __future__ import annotations

import json
import time
from pathlib import Path

from enterprise_rag.service import EnterpriseRAG
from enterprise_rag.vector_store import VectorStore
from enterprise_rag.config import EVALUATION_FILE

ROOT = Path(__file__).resolve().parents[1]
UNANSWERABLE_FILE = ROOT / "data" / "evaluation" / "unanswerable.json"
REFUSAL_PHRASE = "I don't have enough information in the indexed documents to answer that."


def benchmark_questions(assistant: EnterpriseRAG, questions: list[str]) -> tuple[float, list[str]]:
    timings: list[float] = []
    answers: list[str] = []
    for question in questions:
        start = time.perf_counter()
        answer = assistant.answer(question).answer
        elapsed = time.perf_counter() - start
        timings.append(elapsed)
        answers.append(answer)
    return sum(timings) / len(timings), answers


def main() -> None:
    store = VectorStore()
    print(f"ChromaDB collection count: {store.collection.count()}")

    assistant = EnterpriseRAG()
    evaluation = json.loads(EVALUATION_FILE.read_text(encoding="utf-8"))
    five_questions = [case["question"] for case in evaluation[:5]]

    avg_latency, _ = benchmark_questions(assistant, five_questions)
    print(f"Average end-to-end latency (5 questions): {avg_latency:.3f} s")

    start = time.perf_counter()
    # Reuse the production evaluation command's exact evaluation workload.
    from enterprise_rag.cli import evaluate
    evaluate()
    evaluation_elapsed = time.perf_counter() - start
    print(f"Evaluation runtime ({len(evaluation)} questions): {evaluation_elapsed:.3f} s")

    unanswerable = json.loads(UNANSWERABLE_FILE.read_text(encoding="utf-8"))
    refusal_count = 0
    for case in unanswerable:
        answer = assistant.answer(case["question"]).answer
        refused = REFUSAL_PHRASE.lower() in answer.lower()
        refusal_count += int(refused)
        print(f"{'REFUSED' if refused else 'ANSWERED'} | {case['question']}")

    refusal_rate = refusal_count / len(unanswerable)
    print(
        f"Unanswerable refusal accuracy: {refusal_count}/{len(unanswerable)} "
        f"({refusal_rate:.1%})"
    )


if __name__ == "__main__":
    main()
