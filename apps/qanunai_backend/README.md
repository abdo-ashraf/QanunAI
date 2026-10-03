# Backend

FastAPI backend managed with `uv` and organized with DDD-inspired layers:

- `domain/`
- `application/`
- `infrastructure/`
- `presentation/`

Run locally:

```bash
python -m uv sync
python -m uv run uvicorn presentation.app:app --reload
```

## RAG API

The RAG engine uses Haystack pipelines with Qdrant for dense retrieval and
OpenAI-compatible APIs for embeddings and generation. Copy the repository
root's `.env.example` to `.env` and set the API key and service URLs. The
`EMBEDDING_BASE_URL` and `GENERATOR_BASE_URL` values are passed independently
to the corresponding Haystack components. Set `RETRIEVER_TOP_K` to control how
many documents are passed to the prompt (default: `5`). Start the backend and
Qdrant together from the repository root:

```bash
cp .env.example .env
docker compose up --build
```

Index documents with `POST /api/v1/rag/documents`:

```json
{"documents": [{"content": "Qdrant is a vector database.", "meta": {"source": "docs"}}]}
```

Ask a question with `POST /api/v1/rag/query`:

```json
{"query": "What is Qdrant?"}
```
