from pathlib import Path

SUPPORTED_SUFFIXES = {".md", ".txt", ".pdf"}


def read_document(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader

        return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages).strip()
    return path.read_text(encoding="utf-8").strip()


def recursive_chunks(text: str, size: int, overlap: int) -> list[str]:
    """Split readable text near paragraph/sentence/word boundaries."""
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    separators = ("\n\n", "\n", ". ", " ")
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = max((text.rfind(s, start, end) for s in separators), default=-1)
            if boundary > start:
                end = boundary + 1
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks
