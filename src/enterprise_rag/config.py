from pathlib import Path
import os

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

DOCUMENTS_DIR = ROOT / "data" / "documents"
CHROMA_DIR = ROOT / "data" / "chroma"
EVALUATION_FILE = ROOT / "data" / "evaluation" / "questions.json"
COLLECTION_NAME = "enterprise_knowledge"
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150
TOP_K = 3
CHAT_MODEL = os.getenv("RAG_CHAT_MODEL", "llama3.2:3b")
EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "nomic-embed-text")
