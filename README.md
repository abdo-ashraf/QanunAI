# QanunAI

**Arabic legal Q&A over the Egyptian Civil Code of 1948 — with exact article citations.**

QanunAI is a Retrieval-Augmented Generation (RAG) assistant that answers legal
questions by grounding every response in the indexed law text instead of relying
on model memory. It ships as a production-oriented monorepo with a **FastAPI
backend**, a **React chat frontend**, a **pluggable vector-store abstraction**,
and a **full observability stack** (Prometheus + Grafana + Langfuse).

---

## Table of Contents

- [1. Project Overview & Architecture](#1-project-overview--architecture)
  - [Design Philosophy](#design-philosophy)
  - [System Architecture](#system-architecture)
  - [Request Lifecycle](#request-lifecycle)
- [2. Tech Stack](#2-tech-stack)
- [3. Getting Started & Installation](#3-getting-started--installation)
  - [Prerequisites](#prerequisites)
  - [Repository Layout](#repository-layout)
  - [Local Development](#local-development)
  - [Docker Compose](#docker-compose)
  - [Data Versioning (DVC)](#data-versioning-dvc)
  - [Environment Reference](#environment-reference)
- [4. Observability & Monitoring](#4-observability--monitoring)
  - [Grafana](#grafana)
  - [Langfuse](#langfuse)
- [5. Dependency Injection (DI) Architecture](#5-dependency-injection-di-architecture)
- [6. Database Migration Guide: Qudrat VectorDB](#6-database-migration-guide-qudrat-vectordb)

---

## 1. Project Overview & Architecture

QanunAI is a **stateless, retrieval-grounded question-answering service**. A user
asks a legal question in Arabic; the backend embeds the question, retrieves the
most similar chunks from a vector store, filters them by a similarity threshold,
and asks an LLM to answer **using only the retrieved context**. The response
returns both the answer and the source passages (with similarity scores) so the
citation can be verified.

### Core capabilities

| Capability | Description |
| --- | --- |
| **Grounded RAG Q&A** | Answers are constrained to retrieved context via the system prompt. |
| **Pluggable vector store** | `pgvector` (default) or `Qdrant`, selected at runtime by config. |
| **Automatic document ingestion** | On startup the backend parses, chunks, and incrementally indexes files from `stores/`. |
| **Source attribution** | Retrieved documents and scores are returned with every answer. |
| **Git-managed prompts** | System/user prompts live in version-controlled YAML. |
| **Bilingual UI** | Arabic (RTL, default) and English (LTR) with a runtime toggle. |
| **Production observability** | Prometheus metrics, a provisioned Grafana dashboard, and opt-in Langfuse LLM tracing. |

### Design Philosophy

- **DDD-inspired layering.** `domain` holds framework-agnostic entities and
  rules; `application` orchestrates use-cases; `infrastructure` contains
  adapters and integrations; `presentation` exposes FastAPI routers and DTOs.
  Dependencies point **inward** — the domain knows nothing about FastAPI,
  Haystack, or any database.
- **Depend on abstractions.** The application depends on the `RagEngine`
  protocol, never on a concrete vector store. Swapping databases is a factory
  change, not a rewrite.
- **Incremental by default.** Ingestion uses a content-hash manifest so only new
  or changed files are re-embedded on startup.
- **Observable and privacy-aware.** Metrics are low-cardinality and
  content-free; LLM content tracing is strictly opt-in.

### System Architecture

```mermaid
flowchart LR
    subgraph Client["🖥️ Client"]
        Browser["React 19 + Vite SPA<br/>ai-elements chat UI"]
    end

    subgraph Backend["⚙️ FastAPI Backend — DDD Layers"]
        API["Presentation<br/>/api/v1/rag · /health · /metrics"]
        SVC["Application<br/>RagService · HealthService"]
        DOM["Domain<br/>KnowledgeDocument · LegalQuestion"]
        RAG["Infrastructure · RAG<br/>HaystackRagEngineBase"]
        ING["Infrastructure · Ingestion<br/>stores_ingestion"]
    end

    subgraph Stores["🗄️ Vector Stores"]
        PG[("pgvector<br/>PostgreSQL 17")]
        QD[("Qdrant<br/>optional profile")]
    end

    subgraph Providers["🧠 Model Providers (OpenAI-compatible)"]
        EMB["Embeddings API"]
        LLM["Chat Completions API"]
    end

    subgraph Obs["📊 Observability"]
        PROM["Prometheus"]
        GRAF["Grafana"]
        LF["Langfuse"]
        LFE["Langfuse Exporter"]
        NODE["Node Exporter"]
        PGEX["Postgres Exporter"]
    end

    FILES[("stores/<br/>pdf · md · docx · csv …")]

    Browser -- "HTTP / JSON" --> API
    API --> SVC
    SVC --> DOM
    SVC --> RAG
    RAG -- "embed" --> EMB
    RAG -- "generate" --> LLM
    RAG --> PG
    RAG -. "RAG_BACKEND=qdrant" .-> QD
    FILES --> ING --> RAG
    API -- "/metrics" --> PROM
    RAG -- "OTLP spans" --> LF
    LF --> LFE -- "/metrics" --> PROM
    NODE --> PROM
    PGEX --> PROM
    PROM --> GRAF
```

### Request Lifecycle

1. **Ingestion (startup).** `index_stores_files()` walks `stores/`, converts each
   file with the matching Haystack converter, splits it into word-based chunks,
   and indexes only files whose content hash changed.
2. **Query.** `POST /api/v1/rag/query` → `RagService.answer_question()` →
   `RagEngine.answer()`:
   `OpenAITextEmbedder → retriever → ScoreThresholdFilter → ChatPromptBuilder → OpenAIChatGenerator`.
3. **Filtering.** Documents below `RETRIEVER_SCORE_THRESHOLD` are dropped before
   reaching the prompt; results are capped by `RETRIEVER_TOP_K`.
4. **Response.** The answer plus accepted source documents/scores are returned
   and rendered in the chat UI. Provider outages surface as **HTTP 503** via the
   `AssistantUnavailableError` handler.

---

## 2. Tech Stack

| Component | Usage / Role |
| --- | --- |
| **Python 3.12** | Backend language/runtime. |
| **FastAPI** | HTTP API framework; routers, DI, exception handling. |
| **uv** | Python dependency, lockfile, and virtualenv management. |
| **Pydantic / pydantic-settings** | Typed configuration and request/response validation. |
| **Haystack** | RAG pipeline orchestration (embedders, retrievers, generators). |
| **pgvector (PostgreSQL 17)** | Default vector store (`PgvectorDocumentStore`, HNSW indexing). |
| **Qdrant** | Optional vector store (`RAG_BACKEND=qdrant`). |
| **OpenAI-compatible APIs** | Embeddings and chat completions (OpenAI, Ollama, or any compatible endpoint). |
| **prometheus-client** | Application metrics exposed at `/metrics`. |
| **Langfuse** | Opt-in LLM/pipeline tracing and evaluation observability. |
| **React 19 + Vite** | Frontend SPA framework and dev/build tooling. |
| **TypeScript** | Type safety across the frontend. |
| **TanStack Query** | Server-state management, mutations, polling. |
| **Zod** | Runtime validation of API responses at the client boundary. |
| **shadcn/ui + ai-elements** | Accessible UI primitives and AI chat components. |
| **Tailwind CSS v4** | Utility-first styling. |
| **Docker & Docker Compose** | Local/dev deployment of app + observability stack. |
| **DVC** | Data version control for the `stores/` corpus. |
| **pre-commit + GitHub Actions** | Hooks and CI (Ruff lint/format, import validation). |

---

## 3. Getting Started & Installation

### Prerequisites

| Tool | Version | Notes |
| --- | --- | --- |
| **Python** | `>= 3.12` | Backend runtime (see `.python-version`). |
| **uv** | latest | `python -m pip install uv`. |
| **Node.js** | `>= 20` | Frontend build/runtime. |
| **npm** | bundled with Node | Dependency management. |
| **Docker** | latest | Required for Compose workflows. |
| **Docker Compose** | v2 | `docker compose` subcommand. |
| **Git** | latest | Source control. |
| **DVC** | optional | Only needed to pull/push `stores/` data. |
| **Embeddings + Chat provider** | — | Any OpenAI-compatible API, or a local Ollama instance. |

### Repository Layout

```
QanunAI/
├── apps/
│   ├── qanunai_backend/          # FastAPI + Haystack service (DDD layers)
│   │   ├── src/{domain,application,infrastructure,presentation}/
│   │   ├── prompts/              # system.yml + user.yml (Git-managed)
│   │   ├── Dockerfile
│   │   └── .env.example
│   └── qanunai_frontend/         # React + Vite + TypeScript SPA
│       └── src/features/legal-assistant/
├── monitoring/                   # Prometheus, Grafana, Langfuse exporter
├── stores/                       # Source documents (DVC-tracked, not Git)
├── docker-compose.yml
└── README.md
```

### Local Development

**1. Clone the repository**

```bash
git clone <repository-url> QanunAI
cd QanunAI
```

**2. Configure environment variables**

```bash
cp apps/qanunai_backend/.env.example apps/qanunai_backend/.env
# Edit the file and set your API keys / endpoints
```

> The backend reads configuration **only from process environment variables**; it
> never loads `.env` itself. Locally it is injected via `uv run --env-file .env`.

**3. Install backend dependencies and run the API**

```bash
cd apps/qanunai_backend
python -m uv sync
python -m uv run --env-file .env uvicorn presentation.app:app --reload --port 8000
```

**4. Install frontend dependencies and run the dev server** *(separate terminal)*

```bash
cd apps/qanunai_frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Open <http://localhost:5173>. The Vite dev server proxies `/api` and `/health`
to `http://localhost:8000`, so no CORS setup is needed in development.

> **pgvector locally:** the default backend expects a PostgreSQL instance with the
> pgvector extension. The simplest way to get one is `docker compose up postgres`.
> Alternatively set `RAG_BACKEND=qdrant` and point `QDRANT_URL` at a running
> Qdrant instance.

**Test the API directly:**

```bash
# Ask a question
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query":"ما هو سن الرشد المدني؟"}'

# Index documents manually
curl -X POST http://localhost:8000/api/v1/rag/documents \
  -H "Content-Type: application/json" \
  -d '{"documents":[{"content":"...","meta":{"source":"manual"}}]}'
```

### Docker Compose

The Compose stack starts the backend, PostgreSQL (pgvector), **and** the full
monitoring stack.

```bash
cp apps/qanunai_backend/.env.example apps/qanunai_backend/.env
# edit apps/qanunai_backend/.env with your API keys
docker compose up --build
```

| Service | URL | Purpose |
| --- | --- | --- |
| Backend API | <http://localhost:8000> | FastAPI app (`/metrics`, `/health`, `/api/v1/rag`) |
| API docs | <http://localhost:8000/docs> | OpenAPI/Swagger UI |
| Grafana | <http://localhost:3000> | Dashboards (`admin` / `admin`) |
| Prometheus | <http://localhost:9090> | Metrics scraping & storage |
| PostgreSQL | `localhost:5432` | pgvector store |
| Qdrant (optional) | <http://localhost:6333> | Enable with the `qdrant` profile |

To use Qdrant instead of pgvector:

```bash
# set RAG_BACKEND=qdrant and QDRANT_URL=http://qdrant:6333 in .env, then:
docker compose --profile qdrant up --build
```

Compose injects `apps/qanunai_backend/.env` via `env_file:` and overrides the
container-network values (`RAG_BACKEND`, `PG_CONN_STR`, `EMBEDDING_BASE_URL`),
so the same `.env` works for both local and Docker runs.

### Data Versioning (DVC)

`stores/` holds the source corpus (`.txt`, `.md`, `.pdf`, `.csv`, `.json`,
`.html`, `.docx`, `.pptx`, `.xlsx`) that the backend parses, chunks, and indexes
on startup. It is versioned with DVC (local remote), not Git.

```bash
# Restore the data after cloning
dvc pull   # requires the DVC binary: apps/qanunai_backend/.venv/bin/dvc

# After changing files in stores/
dvc add stores && dvc push
```

The local DVC remote is configured in `.dvc/config`. On startup the backend walks
`stores/`, converts each parsable file, splits it into word-based chunks, and
indexes only new or changed files (tracked through an indexing manifest).
Unsupported or unparsable files are logged and skipped.

### Environment Reference

All variables are read by the backend from the process environment (backend:
`apps/qanunai_backend/src/application/config.py`).

| Variable | Default | Description |
| --- | --- | --- |
| `RAG_BACKEND` | `pgvector` | Vector store backend: `pgvector` or `qdrant`. |
| `EMBEDDING_API_KEY` | — | API key for the embeddings endpoint. |
| `EMBEDDING_BASE_URL` | — | Base URL of the embeddings provider. |
| `EMBEDDING_MODEL` | `nomic-embed-text-v2-moe:latest` | Embedding model name. |
| `EMBEDDING_DIM` | `768` | Embedding dimension (must match the store). |
| `GENERATOR_API_KEY` | — | API key for the chat completions endpoint. |
| `GENERATOR_BASE_URL` | — | Base URL of the chat provider. |
| `GENERATOR_MODEL` | `gpt-4o-mini` | Chat model name. |
| `RETRIEVER_TOP_K` | `5` | Max documents passed to the prompt. |
| `RETRIEVER_SCORE_THRESHOLD` | `0.7` | Minimum similarity score to keep a document. |
| `CORS_ALLOW_ORIGINS` | `http://localhost:5173` | Comma-separated allowed browser origins. |
| `PG_CONN_STR` | `postgresql://postgres:postgres@localhost:5432/postgres` | pgvector connection string. |
| `PG_TABLE_NAME` | `qanunai_documents` | pgvector table name. |
| `QDRANT_URL` | `http://qdrant:6333` | Qdrant endpoint (when `RAG_BACKEND=qdrant`). |
| `QDRANT_COLLECTION` | `qanunai_documents` | Qdrant collection name. |
| `QDRANT_API_KEY` | — | Qdrant API key (optional; blank becomes `None`). |
| `STORES_PATH` | `./stores` | Corpus directory to ingest. |
| `STORES_INDEX_ON_STARTUP` | `true` | Index `stores/` during startup. |
| `STORES_CHUNK_SIZE` | `200` | Words per chunk. |
| `STORES_CHUNK_OVERLAP` | `20` | Overlapping words between chunks. |
| `STORES_MANIFEST_PATH` | — | Path to the incremental indexing manifest. |
| `PROMPTS_PATH` | `prompts` | Directory containing `system.yml` / `user.yml`. |
| `LANGFUSE_TRACING_ENABLED` | `false` | Opt-in LLM/pipeline tracing. |
| `LANGFUSE_PUBLIC_KEY` | — | Langfuse public key. |
| `LANGFUSE_SECRET_KEY` | — | Langfuse secret key. |
| `LANGFUSE_BASE_URL` | `https://cloud.langfuse.com` | Langfuse host (Cloud or self-hosted). |
| `LANGFUSE_SERVICE_NAME` | `qanunai-backend` | Trace service name. |

**Frontend** (`apps/qanunai_frontend/.env`):

| Variable | Default | Description |
| --- | --- | --- |
| `VITE_API_BASE_URL` | *(empty)* | Backend origin. Empty uses the Vite proxy / same-origin. |

---

## 4. Observability & Monitoring

QanunAI is observable at two levels: **infrastructure/metrics** (Prometheus +
Grafana) and **LLM pipeline traces** (Langfuse).

- **Tracking & logging.** The backend logs to standard output/stderr
  (`logging`), emits low-cardinality Prometheus metrics, and (when enabled)
  ships pipeline spans to Langfuse. The `langfuse-exporter` bridges Langfuse's
  Metrics API into Prometheus so LLM cost/token/latency data appears on the same
  dashboards as HTTP and infrastructure metrics.
- **Privacy by design.** Application metrics never include document contents or
  identifiers. The Langfuse exporter intentionally exports only aggregates
  (observations, tokens, latency, cost) — not prompts, trace IDs, user IDs, or
  session IDs.

Start the full stack with `docker compose up --build`. The monitoring services:

| Service | Image | Role |
| --- | --- | --- |
| **Node Exporter** | `prom/node-exporter` | Host CPU, memory, filesystem, network metrics. |
| **Postgres Exporter** | `prometheuscommunity/postgres-exporter` | PostgreSQL metrics (internal to the network; scraped at `postgres-exporter:9187`). |
| **Langfuse Exporter** | local build (`monitoring/langfuse-exporter`) | Converts Langfuse Metrics API v2 data into Prometheus metrics. |
| **Prometheus** | `prom/prometheus` | Scrapes every 15s, retains metrics for 15 days. |
| **Grafana** | `grafana/grafana` | Prometheus provisioned as the default datasource. |

### Grafana

Grafana ships with Prometheus provisioned as its default datasource and the
**RAG MLOps Observability** dashboard pre-loaded under the **MLOps** folder
(`monitoring/grafana/dashboards/rag-mlops-overview.json`).

**Dashboard screenshots**

The **1. API & Transport** row — request rate, latency percentiles, and error
rate by status:

![Grafana dashboard — API & Transport](./assets/Grafana_dashboard_1.png)

The **2. Infrastructure & Resources** row — host CPU and process memory:

![Grafana dashboard — Infrastructure & Resources](./assets/Grafana_dashboard_2.png)

The **3. RAG & Model Execution** row — Langfuse observations, model latency, and
token throughput:

![Grafana dashboard — RAG & Model Execution](./assets/Grafana_dashboard_3.png)

The **4. Retrieval Quality** row — mean top-k similarity, score-threshold
acceptance rate, and zero-result query rate:

![Grafana dashboard — Retrieval Quality](./assets/Grafana_dashboard_4.png)

The dashboard is organized into four rows:

| Row | Panels |
| --- | --- |
| **1. API & Transport** | Request rate (RPS), latency p50/p95/p99, HTTP error rate, responses by status. |
| **2. Infrastructure & Resources** | Host CPU busy (node-exporter), process resident memory. |
| **3. RAG & Model Execution** | Langfuse observations/sec, observation & model latency, input/output tokens, retrieved document count p50. |
| **4. Retrieval Quality** | Mean top-k similarity, score-threshold acceptance rate, zero-result query rate, LLM token totals. |

HTTP request rate, latency, and status panels are populated by the backend
`/metrics` endpoint. RAG/token/cost panels come from the Langfuse exporter,
which polls `/api/public/v2/metrics` every 60 seconds over a configurable
rolling window and exposes a Prometheus-compatible `/metrics` endpoint on the
Compose network. The **Retrieval Quality** row reports mean top-k similarity,
score-threshold acceptance rate, and zero-result query rate from the backend
retrieval metrics (based on retriever candidates *before* and *after* threshold
filtering).

**Recommended Grafana panels for QanunAI** (if you extend the dashboard):

- **Retrieval health** — `rag_retrieval_accepted_documents_total` ÷
  `rag_retrieval_candidates_total` (acceptance rate), `rag_retrieval_empty_queries_total`.
- **Answer quality proxy** — p50/p95 of `rag_retrieved_documents` (a sudden drop
  usually indicates retrieval or corpus issues).
- **Provider reliability** — rate of HTTP 503s on `/api/v1/rag/query` plus
  Langfuse exporter `up` gauge to spot embedding/LLM outages.

> **Credentials:** the defaults (`admin`/`admin`) and the PostgreSQL password are
> for local development only. Override them for any non-local deployment.

### Langfuse

Langfuse integration is **opt-in**. Enable it by setting:

```dotenv
LANGFUSE_TRACING_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com   # or a self-hosted instance
LANGFUSE_SERVICE_NAME=qanunai-backend
```

When enabled, the `LangfuseTracer` is registered with Haystack and sends pipeline
traces — component inputs/outputs, prompts, retrieved documents, and model
responses — to Langfuse. Queued spans are flushed on application shutdown.

> **Content tracing warning:** traces can contain user questions, retrieved
> legal text, prompts, and model responses. Enable content tracing only when
> sending that data to Langfuse is permitted.

**Langfuse screenshots**

The Langfuse dashboard gives an aggregate view of traces, latency, and cost:

![Langfuse dashboard](./assets/langfuse_dashboard.png)

Individual traces expose the full RAG pipeline — prompt, retrieved documents,
and model response — for debugging and evaluation:

![Langfuse single trace view](./assets/Langfuse_one_trace_view.png)

The bundled `langfuse-exporter` also surfaces aggregates in Grafana. It requires
Langfuse **Metrics API v2** (Langfuse Cloud and self-hosted v4+); self-hosted v3
uses the v1 API and is incompatible with the default exporter query.

---

## 5. Dependency Injection (DI) Architecture

QanunAI uses **constructor injection plus FastAPI's dependency system** to keep
services, repositories, and configuration decoupled and swappable.

### Configuration injection

`Settings` is a `pydantic-settings` model, and `get_settings()` is wrapped in
`functools.lru_cache` so a single validated configuration instance is created
and reused process-wide. Infrastructure components receive typed, validated
settings rather than reading raw environment variables.

```python
from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### Service and engine injection

The application layer depends on the `RagEngine` **Protocol**, not on a concrete
implementation. The presentation layer wires dependencies through FastAPI's
`Depends`:

```python
# presentation/api/v1/rag.py
@lru_cache
def get_rag_engine() -> RagEngine:          # cached singleton
    return create_rag_engine()              # factory chooses pgvector / qdrant

def get_rag_service() -> RagService:        # per-request use-case
    return RagService(get_rag_engine())

@router.post("/query", response_model=QueryResponse)
def query_rag(
    request: QueryRequest,
    service: Annotated[RagService, Depends(get_rag_service)],
) -> QueryResponse: ...
```

The **factory** is the single place that knows which concrete adapter to build,
selected from configuration:

```python
# infrastructure/rag/factory.py
def create_rag_engine() -> RagEngine:
    settings = get_settings()
    if settings.rag_backend == "qdrant":
        return HaystackQdrantRagEngine()
    return HaystackPgvectorRagEngine()
```

### Why this matters

| Benefit | How it's achieved |
| --- | --- |
| **Modularity** | `RagService` and endpoints never import a concrete store; they depend on the `RagEngine` protocol. |
| **Testability** | Inject a fake/in-memory `RagEngine` (`InMemoryKnowledgeRepository` shows the pattern) without touching databases. |
| **Maintainability** | New backends are added in one factory branch; no call sites change. |
| **Configuration decoupling** | Validated `Settings` are injected, not read ad-hoc throughout the code. |
| **Lifecycle control** | `@lru_cache` gives engine-level singletons; `Depends` scopes service instantiation per request. |

```mermaid
flowchart TD
    Router["Presentation · /rag router"] -->|Depends| SvcFactory["get_rag_service()"]
    SvcFactory --> Svc["RagService(engine: RagEngine)"]
    Svc -->|Protocol| Engine["RagEngine"]
    Engine -.implements.-> PG["HaystackPgvectorRagEngine"]
    Engine -.implements.-> QD["HaystackQdrantRagEngine"]
    Factory["create_rag_engine()"] -->|RAG_BACKEND| PG
    Factory -->|RAG_BACKEND| QD
    SvcFactory --> Factory
    Settings["get_settings() · lru_cache"] --> Factory
    Settings --> PG
    Settings --> QD
```

---

## 6. Database Migration Guide: Qudrat VectorDB

The vector layer is intentionally abstracted so a new database can be introduced
without touching the application or presentation layers. This section explains
the abstraction and how to plug in **Qudrat vectorDB**.

### The abstraction contract

The application only knows the `RagEngine` protocol
(`application/services/rag_service.py`):

```python
class RagEngine(Protocol):
    def index(self, documents: list[KnowledgeDocument]) -> int: ...
    def answer(self, query: str) -> RagAnswer: ...
```

The Haystack implementation builds on a shared base that wires two pipelines and
accepts **any document store + retriever** pair
(`infrastructure/rag/haystack_base.py`):

```python
class HaystackRagEngineBase(RagEngine):
    def __init__(self, document_store, retriever) -> None:
        # indexing pipeline:  doc_embedder -> writer(document_store)
        # RAG pipeline:       text_embedder -> retriever -> score_filter
        #                     -> prompt_builder -> llm
        ...
```

Two concrete adapters already demonstrate the pattern:

- `HaystackPgvectorRagEngine` — `PgvectorDocumentStore` + `PgvectorEmbeddingRetriever`
- `HaystackQdrantRagEngine` — `QdrantDocumentStore` + `QdrantEmbeddingRetriever`

### Option A — Reuse the Haystack base (recommended)

If Qudrat provides (or you can wrap in) a Haystack-compatible **document store**
and **embedding retriever**, this is the smallest change.

**Step 1 — Add Qudrat settings** in `application/config.py`:

```python
rag_backend: Literal["pgvector", "qdrant", "qudrat"] = "pgvector"

qudrat_url: str = "http://qudrat:6333"
qudrat_collection: str = "qanunai_documents"
qudrat_api_key: SecretStr | None = None
```

**Step 2 — Implement the adapter** at
`infrastructure/rag/haystack_qudrat_engine.py`, mirroring the existing engines:

```python
from application.config import get_settings
from infrastructure.rag.haystack_base import HaystackRagEngineBase


class HaystackQudratRagEngine(HaystackRagEngineBase):
    def __init__(self) -> None:
        settings = get_settings()
        document_store = QudratDocumentStore(          # your wrapper
            url=settings.qudrat_url,
            index=settings.qudrat_collection,
            embedding_dim=settings.embedding_dim,
        )
        retriever = QudratEmbeddingRetriever(          # your wrapper
            document_store=document_store,
            top_k=settings.retriever_top_k,
        )
        super().__init__(document_store=document_store, retriever=retriever)
```

**Step 3 — Register it in the factory** (`infrastructure/rag/factory.py`):

```python
if settings.rag_backend == "qudrat":
    return HaystackQudratRagEngine()
```

**Step 4 — Configure and run.** Update `.env` / Compose:

```dotenv
RAG_BACKEND=qudrat
QUDRAT_URL=http://qudrat:6333
QUDRAT_COLLECTION=qanunai_documents
QUDRAT_API_KEY=
EMBEDDING_DIM=768     # must match your Qudrat collection dimension
```

```bash
docker compose up --build
```

That's the entire integration: the routers, `RagService`, ingestion pipeline,
metrics, and tracing all work unchanged because they depend on `RagEngine`, not
on the store.

### Option B — Implement `RagEngine` directly

If Qudrat's client is a native SDK (not Haystack-shaped), implement the protocol
directly. This keeps Haystack out of the Qudrat path but you own embedding,
filtering, and prompt assembly:

```python
class QudratRagEngine(RagEngine):
    def __init__(self) -> None:
        self._settings = get_settings()
        self._client = QudratClient(self._settings.qudrat_url, api_key=...)

    def index(self, documents: list[KnowledgeDocument]) -> int:
        # embed via EMBEDDING_* config, upsert vectors + metadata,
        # return the number written
        ...

    def answer(self, query: str) -> RagAnswer:
        # embed query -> search -> apply RETRIEVER_SCORE_THRESHOLD
        # -> build prompt from prompts/system.yml + user.yml
        # -> generate -> return RagAnswer(answer, documents)
        ...
```

Register the same way in `create_rag_engine()`. Reuse
`record_retrieval_quality()` / `record_retrieved_documents()` so Qudrat queries
still populate the Grafana **Retrieval Quality** row.

### Migration checklist

- [ ] **Dimension parity.** Set `EMBEDDING_DIM` to Qudrat's collection dimension;
      a mismatch silently corrupts results or errors at write time.
- [ ] **Distance metric.** Match `vector_function`/similarity (the pgvector engine
      uses cosine); confirm Qudrat's scoring aligns with `RETRIEVER_SCORE_THRESHOLD`.
- [ ] **Index configuration.** Provide HNSW/quantization parameters equivalent to
      pgvector's HNSW strategy for comparable latency.
- [ ] **Re-ingestion.** Qudrat starts empty; re-run startup ingestion (or
      `POST /api/v1/rag/documents`) and, if reusing the manifest, clear it so files
      are re-embedded.
- [ ] **Secrets.** Load the Qudrat API key via `SecretStr`; never bake it into
      images or Compose files.
- [ ] **Health & metrics.** Confirm Prometheus scrapes the backend `/metrics` and
      that Qudrat query latency appears in Grafana after migration.
- [ ] **Tracing.** Keep `LANGFUSE_TRACING_ENABLED` behavior intact so retrieval
      quality remains observable end to end.

---

## License

See [`LICENSE`](./LICENSE) for details.
