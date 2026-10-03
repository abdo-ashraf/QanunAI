from dataclasses import dataclass
from typing import Protocol

from domain.entities.knowledge_document import KnowledgeDocument


@dataclass(frozen=True)
class RetrievedDocument:
    content: str
    score: float | None
    meta: dict[str, object]


@dataclass(frozen=True)
class RagAnswer:
    answer: str
    documents: list[RetrievedDocument]


class RagEngine(Protocol):
    def index(self, documents: list[KnowledgeDocument]) -> int: ...

    def answer(self, query: str) -> RagAnswer: ...


class RagService:
    def __init__(self, engine: RagEngine) -> None:
        self._engine = engine

    def index_documents(self, documents: list[KnowledgeDocument]) -> int:
        return self._engine.index(documents)

    def answer_question(self, query: str) -> RagAnswer:
        return self._engine.answer(query)
