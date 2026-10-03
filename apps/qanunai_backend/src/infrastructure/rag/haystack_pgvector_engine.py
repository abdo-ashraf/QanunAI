from haystack.utils import Secret
from haystack_integrations.components.retrievers.pgvector import (
    PgvectorEmbeddingRetriever,
)
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore

from application.config import get_settings
from infrastructure.rag.haystack_base import HaystackRagEngineBase


class HaystackPgvectorRagEngine(HaystackRagEngineBase):
    def __init__(self) -> None:
        settings = get_settings()
        document_store = PgvectorDocumentStore(
            connection_string=Secret.from_token(settings.pg_conn_str),
            table_name=settings.pg_table_name,
            embedding_dimension=settings.embedding_dim,
            vector_function="cosine_similarity",
            search_strategy="hnsw",
            recreate_table=False,
        )
        retriever = PgvectorEmbeddingRetriever(
            document_store=document_store,
            top_k=settings.retriever_top_k,
        )
        super().__init__(document_store=document_store, retriever=retriever)
