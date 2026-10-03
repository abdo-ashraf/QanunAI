# Backend

FastAPI backend managed with `uv` and organized with DDD-inspired layers:

- `domain/`
- `application/`
- `infrastructure/`
- `presentation/`

Run locally:

```bash
cp .env.example .env   # fill in your API keys
python -m uv sync
python -m uv run --env-file .env uvicorn presentation.app:app --reload
```

## RAG API

The RAG engine uses Haystack pipelines with Qdrant for dense retrieval and
OpenAI-compatible APIs for embeddings and generation. Copy `.env.example` to
`.env` and set the API keys and service URLs. The app reads configuration only
from process environment variables (see `src/application/config.py`); it never
loads the `.env` file itself. The `EMBEDDING_BASE_URL` and `GENERATOR_BASE_URL`
values are passed independently to the corresponding Haystack components. Set
`RETRIEVER_TOP_K` to control how many documents are passed to the prompt
(default: `5`). Start the backend and Qdrant together from the repository root:

```bash
cp apps/qanunai_backend/.env.example apps/qanunai_backend/.env
docker compose up --build
```

Compose injects `apps/qanunai_backend/.env` into the container via `env_file:`
and overrides the container-network values (`QDRANT_URL`,
`EMBEDDING_BASE_URL`) in its `environment:` block, so the same `.env` works for
both local runs and Docker.

Index documents with `POST /api/v1/rag/documents`:

```json
{"documents": [{"content": "Qdrant is a vector database.", "meta": {"source": "docs"}}]}
```

Ask a question with `POST /api/v1/rag/query`:

```json
{"query": "What is Qdrant?"}
```

## Langfuse tracing

RAG pipeline tracing is opt-in. Set the following variables in `.env` to send
Haystack pipeline traces, component inputs/outputs, prompts, retrieved
documents, and model responses to Langfuse:

```dotenv
LANGFUSE_TRACING_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
LANGFUSE_SERVICE_NAME=qanunai-backend
```

`LANGFUSE_BASE_URL` can point to Langfuse Cloud or a self-hosted Langfuse
instance.
Content tracing is enabled only when `LANGFUSE_TRACING_ENABLED` is `true`.
Because traces can contain user questions, retrieved legal text, prompts, and
model responses, enable it only when sending that data to Langfuse is
permitted. The backend flushes queued spans during shutdown.
