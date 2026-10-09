import logging

from haystack import Document, Pipeline, component
from haystack.components.builders import ChatPromptBuilder
from haystack.components.embedders import OpenAIDocumentEmbedder, OpenAITextEmbedder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.writers import DocumentWriter
from haystack.core.errors import PipelineRuntimeError
from haystack.dataclasses import ChatMessage
from haystack.utils import Secret

from application.config import get_settings
from application.services.rag_service import RagAnswer, RagEngine, RetrievedDocument
from domain.entities.knowledge_document import KnowledgeDocument
from domain.errors import AssistantUnavailableError
from infrastructure.observability.metrics import (
    record_retrieval_quality,
    record_retrieved_documents,
)
from infrastructure.rag.prompt_loader import load_rag_prompt_messages

logger = logging.getLogger(__name__)

# Query pipeline components backed by external embedding/LLM providers. When
# one of them fails, the provider is unavailable (outage, exhausted credits,
# malformed response) and the assistant cannot answer right now.
_PROVIDER_COMPONENTS = frozenset({"text_embedder", "llm"})


@component
class ScoreThresholdFilter:
    def __init__(self, threshold: float) -> None:
        self.threshold = threshold

    @component.output_types(documents=list[Document])
    def run(self, documents: list[Document]) -> dict[str, list[Document]]:
        return {
            "documents": [
                document
                for document in documents
                if document.score is not None and document.score >= self.threshold
            ]
        }


class HaystackRagEngineBase(RagEngine):
    """Shared Haystack RAG pipeline; subclasses provide the document store retriever."""

    def __init__(self, document_store, retriever) -> None:
        settings = get_settings()
        embedding_api_key = Secret.from_token(
            settings.embedding_api_key.get_secret_value()
        )
        generator_api_key = Secret.from_token(
            settings.generator_api_key.get_secret_value()
        )
        self._document_store = document_store

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
        self._rag_pipeline.add_component("retriever", retriever)
        self._rag_pipeline.add_component(
            "score_threshold_filter",
            ScoreThresholdFilter(settings.retriever_score_threshold),
        )
        self._rag_pipeline.add_component(
            "prompt_builder",
            ChatPromptBuilder(template=load_rag_prompt_messages(settings.prompts_path)),
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
        self._rag_pipeline.connect(
            "retriever.documents", "score_threshold_filter.documents"
        )
        self._rag_pipeline.connect(
            "score_threshold_filter.documents", "prompt_builder.documents"
        )
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
        try:
            result = self._rag_pipeline.run(
                {
                    "text_embedder": {"text": query},
                    "prompt_builder": {"query": query},
                },
                include_outputs_from={"retriever", "score_threshold_filter"},
            )
        except PipelineRuntimeError as error:
            if error.component_name in _PROVIDER_COMPONENTS:
                logger.exception(
                    "Query pipeline component %r failed; marking the assistant "
                    "as temporarily unavailable",
                    error.component_name,
                )
                raise AssistantUnavailableError() from error
            raise
        filtered_documents = result["score_threshold_filter"]["documents"]
        record_retrieval_quality(
            [
                document.score
                for document in result["retriever"]["documents"]
                if document.score is not None
            ],
            len(filtered_documents),
        )
        documents = [
            RetrievedDocument(
                content=document.content,
                score=document.score,
                meta=dict(document.meta),
            )
            for document in filtered_documents
        ]
        record_retrieved_documents(len(documents))
        replies: list[ChatMessage] = result["llm"]["replies"]
        return RagAnswer(answer=replies[0].text or "", documents=documents)
