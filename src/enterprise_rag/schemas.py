from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    source: str
    chunk_number: int

    @property
    def label(self) -> str:
        return f"{self.source} · chunk {self.chunk_number}"


@dataclass(frozen=True)
class Answer:
    answer: str
    sources: list[Chunk]
