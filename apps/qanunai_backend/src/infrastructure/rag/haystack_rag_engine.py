from haystack import Document, Pipeline
from haystack.components.builders import ChatPromptBuilder
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.writers import DocumentWriter
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

from application.config import get_settings
from application.services.rag_service import RagAnswer, RagEngine, RetrievedDocument
from domain.entities.knowledge_document import KnowledgeDocument


class HaystackQdrantRagEngine(RagEngine):
    def __init__(self) -> None:
        settings = get_settings()
        embedding_api_key = Secret.from_token(
            settings.embedding_api_key.get_secret_value()
        )
        generator_api_key = Secret.from_token(
            settings.generator_api_key.get_secret_value()
        )
        qdrant_api_key = settings.qdrant_api_key
        qdrant_secret: Secret | None = None
        if qdrant_api_key is not None:
            qdrant_secret = Secret.from_token(qdrant_api_key.get_secret_value())
        self._document_store = QdrantDocumentStore(
            url=settings.qdrant_url,
            api_key=qdrant_secret,
            index=settings.qdrant_collection,
            embedding_dim=settings.embedding_dim,
            recreate_index=False,
        )

        self._indexing_pipeline = Pipeline()
        self._indexing_pipeline.add_component(
            "doc_embedder",
            OpenAIDocumentEmbedder(
                api_key=embedding_api_key,
                model=settings.embedding_model,
                api_base_url=settings.embedding_base_url,
            ),
        )
        self._indexing_pipeline.add_component(
            "writer", DocumentWriter(document_store=self._document_store)
        )
        self._indexing_pipeline.connect("doc_embedder.documents", "writer.documents")

        self._rag_pipeline = Pipeline()
        self._rag_pipeline.add_component(
            "text_embedder",
            OpenAITextEmbedder(
                api_key=embedding_api_key,
                model=settings.embedding_model,
                api_base_url=settings.embedding_base_url,
            ),
        )
        self._rag_pipeline.add_component(
            "retriever",
            QdrantEmbeddingRetriever(
                document_store=self._document_store,
                top_k=settings.retriever_top_k,
            ),
        )
        self._rag_pipeline.add_component(
            "prompt_builder",
            ChatPromptBuilder(
                template=[
                    ChatMessage.from_system(
                        "Answer the query using ONLY the provided context."
                    ),
                    ChatMessage.from_user(
                        "Context:\n"
                        "{% for doc in documents %}- {{ doc.content }}\n{% endfor %}\n"
                        "Query: {{ query }}"
                    ),
                ]
            ),
        )
        self._rag_pipeline.add_component(
            "llm",
            OpenAIChatGenerator(
                api_key=generator_api_key,
                model=settings.generator_model,
                api_base_url=settings.generator_base_url,
            ),
        )
        self._rag_pipeline.connect(
            "text_embedder.embedding", "retriever.query_embedding"
        )
        self._rag_pipeline.connect("retriever.documents", "prompt_builder.documents")
        self._rag_pipeline.connect("prompt_builder.prompt", "llm.messages")

    def index(self, documents: list[KnowledgeDocument]) -> int:
        if not documents:
            return 0

        haystack_documents = [
            Document(content=document.content, meta=document.meta)
            for document in documents
        ]
        result = self._indexing_pipeline.run(
            {"doc_embedder": {"documents": haystack_documents}}
        )
        return int(result["writer"]["documents_written"])

    def answer(self, query: str) -> RagAnswer:
        result = self._rag_pipeline.run(
            {
                "text_embedder": {"text": query},
                "prompt_builder": {"query": query},
            },
            include_outputs_from={"retriever"},
        )
        documents = [
            RetrievedDocument(
                content=document.content,
                score=document.score,
                meta=dict(document.meta),
            )
            for document in result["retriever"]["documents"]
        ]
        replies: list[ChatMessage] = result["llm"]["replies"]
        return RagAnswer(answer=replies[0].text or "", documents=documents)
