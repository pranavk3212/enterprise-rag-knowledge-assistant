# RAG-Based Enterprise Knowledge Assistant

A portfolio-ready Retrieval-Augmented Generation (RAG) system for answering questions from internal documents. It runs entirely on a local machine through Ollama, returns source citations with every answer, and includes a repeatable evaluation harness.

## Project results

| Evaluation set | Top-1 retrieval | Top-3 retrieval | Citation-grounded answers |
| --- | ---: | ---: | ---: |
| 43 answerable questions across 13 AcmeWorks policy documents | **86.0%** | **100.0%** | **100.0%** |
| 10 paraphrased questions | — | **100.0%** | — |
| 10 unanswerable questions | — | — | **90.0% refusal accuracy** |

The AcmeWorks policies are fictional and included only as a demonstration knowledge base.

## What it does

- Ingests `.md`, `.txt`, and `.pdf` documents from `data/documents/`
- Splits them into 900-character recursive chunks with 150-character overlap
- Embeds chunks with local `nomic-embed-text` and stores them locally in Chroma
- Retrieves the top 3 relevant chunks, then prompts the model to answer only from that evidence
- Adds retrieved source labels such as `[security_policy.md · chunk 2]` to every answer
- Evaluates Top-1/Top-3 retrieval, citation grounding, paraphrased queries, and unanswerable-question refusal behavior

## Architecture

```text
Policy documents (.md, .txt, .pdf)
             │
             ▼
Recursive chunking (900 characters, 150-character overlap)
             │
             ▼
nomic-embed-text ──► ChromaDB local vector store
                             │
User question ──► semantic Top-3 retrieval
                             │
                             ▼
                 llama3.2:3b local answer generation
                             │
                             ▼
                    Cited answer in CLI or Streamlit
```

## Quick start

1. Install Python 3.10+ and create a virtual environment.

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -e ".[dev]"
   ```

2. Install [Ollama for Windows](https://ollama.com/download/windows), then open a new PowerShell window and download the free local models:

   ```powershell
   ollama pull llama3.2:3b
   ollama pull nomic-embed-text
   ```

3. Optional: copy `.env.example` to `.env` to override the default local models.
4. Index the included fictional policy knowledge base:

   ```powershell
   rag ingest
   ```

5. Ask a question:

   ```powershell
   rag ask "How long can laptops remain inactive before they must be returned?"
   ```

6. Launch the browser UI:

   ```powershell
   streamlit run app.py
   ```

7. Run the evaluation set:

   ```powershell
   rag evaluate
   ```

## Performance benchmark

Run the benchmark on the same machine where Ollama and the local models are installed:

```powershell
python scripts/benchmark.py
```

The latest local benchmark measured:

| Metric | Result |
| --- | ---: |
| ChromaDB collection count | **13** |
| Average end-to-end latency (5 questions) | **5.554 s** |
| Answerable questions | **43** |
| Top-1 retrieval hit rate | **86.0%** |
| Top-3 retrieval hit rate | **100.0%** |
| Citation-grounded answer rate | **100.0%** |
| Paraphrase Top-3 retrieval hit rate | **100.0%** |
| Unanswerable refusal accuracy | **90.0% (9/10)** |
| Evaluation runtime (53 questions) | **145.522 s (~2m 26s)** |

Timing results are machine-dependent because inference runs locally. The refusal metric is an automated operational check based on the configured refusal response, not a human semantic evaluation.

## Add your own knowledge base

Place `.md`, `.txt`, or `.pdf` files in `data/documents/`, run `rag ingest`, and edit `data/evaluation/questions.json` to match your documents. `rag ingest` recreates the local index so stale document chunks cannot remain in retrieval results. Do not add confidential material to a public repository.

## Local model requirements

This project does not require an OpenAI key or paid API credits. Ollama keeps both the models and prompts on your machine. `llama3.2:3b` is a compact general-purpose model suited to a laptop with at least 8 GB of RAM. On a lower-powered machine, responses can take a little longer.

## Evaluation metrics

- **Top-1 retrieval hit rate:** whether the first retrieved source chunk came from the expected document.
- **Top-3 retrieval hit rate:** whether one of the three retrieved source chunks came from the expected document.
- **Citation-grounded answer rate:** whether the answer includes a citation whose source is the expected document.
- **Paraphrase Top-3 retrieval hit rate:** Top-3 retrieval performance on reworded versions of the answerable questions.
- **Unanswerable refusal accuracy:** the share of intentionally unanswerable questions for which the configured refusal phrase was returned.

These are automated proxy metrics. For a resume-quality "correctly grounded" metric, review a fixed evaluation set and record the proportion of answers that are both factually correct and fully supported by their cited evidence.

## Tech stack

Python · ChromaDB · Ollama · `llama3.2:3b` · `nomic-embed-text` · Streamlit · PyPDF
