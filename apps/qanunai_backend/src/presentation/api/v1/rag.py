from functools import lru_cache
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from application.services.rag_service import RagService
from domain.entities.knowledge_document import KnowledgeDocument
from infrastructure.rag.haystack_rag_engine import HaystackQdrantRagEngine

router = APIRouter(prefix="/rag", tags=["rag"])


@lru_cache
def get_rag_engine() -> HaystackQdrantRagEngine:
    return HaystackQdrantRagEngine()


def get_rag_service() -> RagService:
    return RagService(get_rag_engine())


class DocumentRequest(BaseModel):
    content: str = Field(min_length=1)
    meta: dict[str, Any] = Field(default_factory=dict)


class IndexRequest(BaseModel):
    documents: list[DocumentRequest] = Field(min_length=1)


class IndexResponse(BaseModel):
    documents_written: int


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)


class SourceResponse(BaseModel):
    content: str
    score: float | None
    meta: dict[str, object]


class QueryResponse(BaseModel):
    answer: str
    documents: list[SourceResponse]


@router.post("/documents", response_model=IndexResponse)
def index_documents(
    request: IndexRequest,
    service: Annotated[RagService, Depends(get_rag_service)],
) -> IndexResponse:
    documents = [
        KnowledgeDocument(content=document.content, meta=document.meta)
        for document in request.documents
    ]
    return IndexResponse(documents_written=service.index_documents(documents))


@router.post("/query", response_model=QueryResponse)
def query_rag(
    request: QueryRequest,
    service: Annotated[RagService, Depends(get_rag_service)],
) -> QueryResponse:
    result = service.answer_question(request.query)
    return QueryResponse(
        answer=result.answer,
        documents=[
            SourceResponse(
                content=document.content,
                score=document.score,
                meta=document.meta,
            )
            for document in result.documents
        ],
    )
