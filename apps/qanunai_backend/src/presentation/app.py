from fastapi import FastAPI

from infrastructure.observability.langfuse_tracing import (
    configure_langfuse_tracing,
    flush_langfuse,
)
from presentation.api.v1.health import router as health_router
from presentation.api.v1.rag import router as rag_router

langfuse_client = configure_langfuse_tracing()

app = FastAPI(title="QanunAI API", version="0.1.0")

# app.include_router(health_router, prefix="/api/v1")
app.include_router(health_router)
app.include_router(rag_router, prefix="/api/v1")


@app.on_event("shutdown")
def shutdown_observability() -> None:
    flush_langfuse(langfuse_client)
