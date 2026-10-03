from application.config import get_settings
from application.services.rag_service import RagEngine
from infrastructure.rag.haystack_pgvector_engine import HaystackPgvectorRagEngine
from infrastructure.rag.haystack_qdrant_engine import HaystackQdrantRagEngine


def create_rag_engine() -> RagEngine:
    settings = get_settings()
    if settings.rag_backend == "qdrant":
        return HaystackQdrantRagEngine()
    return HaystackPgvectorRagEngine()
