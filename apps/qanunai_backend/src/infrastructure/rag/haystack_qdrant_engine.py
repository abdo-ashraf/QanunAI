from haystack.utils import Secret
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

from application.config import get_settings
from infrastructure.rag.haystack_base import HaystackRagEngineBase


class HaystackQdrantRagEngine(HaystackRagEngineBase):
    def __init__(self) -> None:
        settings = get_settings()
        qdrant_api_key = settings.qdrant_api_key
        qdrant_secret: Secret | None = None
        if qdrant_api_key is not None:
            qdrant_secret = Secret.from_token(qdrant_api_key.get_secret_value())
        document_store = QdrantDocumentStore(
            url=settings.qdrant_url,
            api_key=qdrant_secret,
            index=settings.qdrant_collection,
            embedding_dim=settings.embedding_dim,
            recreate_index=False,
        )
        retriever = QdrantEmbeddingRetriever(
            document_store=document_store,
            top_k=settings.retriever_top_k,
        )
        super().__init__(document_store=document_store, retriever=retriever)
