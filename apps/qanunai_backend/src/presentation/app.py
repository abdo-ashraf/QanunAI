from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from application.config import get_settings
from domain.errors import AssistantUnavailableError
from infrastructure.ingestion.stores_ingestion import index_stores_files
from infrastructure.observability.langfuse_tracing import (
    configure_langfuse_tracing,
    flush_langfuse,
)
from infrastructure.observability.metrics import install_metrics
from presentation.api.v1.health import router as health_router
from presentation.api.v1.rag import get_rag_engine
from presentation.api.v1.rag import router as rag_router

langfuse_client = configure_langfuse_tracing()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.stores_index_on_startup:
        index_stores_files(get_rag_engine(), Path(settings.stores_path))
    yield
    flush_langfuse(langfuse_client)


app = FastAPI(title="QanunAI API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_allow_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
install_metrics(app)


@app.exception_handler(AssistantUnavailableError)
def assistant_unavailable_handler(
    request: Request, exc: AssistantUnavailableError
) -> JSONResponse:
    """Return a user-facing 503 when the assistant provider is unavailable."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": (
                "The assistant is temporarily unavailable. Please try again later."
            )
        },
    )


# app.include_router(health_router, prefix="/api/v1")
app.include_router(health_router)
app.include_router(rag_router, prefix="/api/v1")
