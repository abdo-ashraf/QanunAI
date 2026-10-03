class InMemoryKnowledgeRepository:
    def __init__(self) -> None:
        self._documents: list[str] = []

    def add(self, document: str) -> None:
        self._documents.append(document)

    def list_all(self) -> list[str]:
        return list(self._documents)
