from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langfuse import Langfuse


def configure_langfuse_tracing() -> Langfuse | None:
    """Enable Haystack tracing in Langfuse when explicitly configured."""
    from application.config import get_settings

    settings = get_settings()
    if not settings.langfuse_tracing_enabled:
        return None

    if settings.langfuse_public_key is None or settings.langfuse_secret_key is None:
        raise RuntimeError(
            "LANGFUSE_TRACING_ENABLED is true, but "
            "LANGFUSE_PUBLIC_KEY or LANGFUSE_SECRET_KEY is missing."
        )

    # Haystack reads this flag while initializing its tracing subsystem.
    import os

    os.environ["HAYSTACK_CONTENT_TRACING_ENABLED"] = "true"

    from haystack import tracing
    from haystack_integrations.tracing.langfuse import LangfuseTracer
    from langfuse import Langfuse

    tracing.tracer.is_content_tracing_enabled = True
    client = Langfuse(
        public_key=settings.langfuse_public_key.get_secret_value(),
        secret_key=settings.langfuse_secret_key.get_secret_value(),
        host=settings.langfuse_host,
    )
    tracing.enable_tracing(
        LangfuseTracer(client, name=settings.langfuse_service_name)
    )
    return client


def flush_langfuse(client: Langfuse | None) -> None:
    """Flush queued spans before the application shuts down."""
    if client is not None:
        client.flush()
