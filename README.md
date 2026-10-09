# QanunAI

Q&A assistant for Arabic legal documents (Egyptian Civil Code of 1948) providing exact article citations.

Monorepo for QanunAI with:

- **Backend**: Python + FastAPI using `uv`, organized with DDD-style layers.
- **Frontend**: React app with feature-based architecture, TanStack Query, shadcn/ui conventions, ai-elements tooling, and Zod validation.
- **Deployment**: Docker + Docker Compose.
- **Automation**: pre-commit + GitHub Actions CI.

## Structure

- `/apps/qanunai_backend`
- `/apps/qanunai_frontend`
- `/docker-compose.yml`
- `/stores` — documents indexed at backend startup (tracked with DVC, not git)

## Stores data (DVC)

The `stores/` folder holds source documents (`.txt`, `.md`, `.pdf`, `.csv`,
`.json`, `.html`, `.docx`, `.pptx`, `.xlsx`) that the backend parses, chunks,
and indexes into the vector store on startup. It is versioned with DVC using a
local remote:

```bash
# restore the data after cloning
dvc pull   # requires the DVC binary: apps/qanunai_backend/.venv/bin/dvc

# after changing files in stores/
dvc add stores && dvc push
```

The DVC remote is configured at `/mnt/d/Eng/playground/QanunAI_dvc_remote`.

On startup the backend walks `stores/`, converts each parsable file with the
matching Haystack converter, splits it into word-based chunks, and indexes only
new or changed files (tracked via `.stores-indexing-manifest.json`). Unsupported
or unparsable files are logged and skipped. Control with `STORES_PATH`,
`STORES_INDEX_ON_STARTUP`, `STORES_CHUNK_SIZE`, `STORES_CHUNK_OVERLAP`, and
`STORES_MANIFEST_PATH`.

Retriever results are limited to `RETRIEVER_TOP_K` documents and then filtered
by `RETRIEVER_SCORE_THRESHOLD` (default `0.7`). Documents without a similarity
score are excluded from the answer context.

RAG prompts are stored as Git-managed YAML files under
`apps/qanunai_backend/prompts/`. The backend loads `system.yml` and `user.yml`
from `PROMPTS_PATH` (default `prompts`; Docker uses `/app/prompts`). Update
those files to change prompt wording, review the diff, and redeploy the backend.

The Grafana dashboard's **Retrieval Quality** row reports mean top-k similarity,
score-threshold acceptance rate, and zero-result query rate from the backend
retrieval metrics. These metrics are based on retriever candidates before and
after threshold filtering and avoid exposing document contents or identifiers.

## Run locally

```bash
cp apps/qanunai_backend/.env.example apps/qanunai_backend/.env
# edit apps/qanunai_backend/.env with your API keys
docker compose up --build
```

## Monitoring

The Compose stack includes:

- **Node Exporter** for host CPU, memory, filesystem, and network metrics.
- **Postgres Exporter** for PostgreSQL metrics from the pgvector-backed database.
- **Langfuse Exporter** for converting Langfuse Metrics API data into Prometheus
  metrics.
- **Prometheus** for scraping and retaining metrics for 15 days.
- **Grafana** with Prometheus provisioned as its default datasource.
- **RAG MLOps Observability** dashboard provisioned in the `MLOps` folder.

Start the application and monitoring stack with:

```bash
docker compose up --build
```

Open the services at:

- Grafana: <http://localhost:3000> (`admin` / `admin`)
- Prometheus: <http://localhost:9090>

The PostgreSQL exporter is intentionally kept internal to the Compose network and
is scraped by Prometheus at `postgres-exporter:9187`. For production deployments,
override the default Grafana credentials and use a non-default PostgreSQL password.

The supplied RAG dashboard is available in Grafana under
**Dashboards > MLOps > RAG MLOps Observability**. HTTP request rate, latency, and
status panels are populated by the backend `/metrics` endpoint. RAG and token
panels use the Langfuse exporter, which polls
`/api/public/v2/metrics` and exposes a Prometheus-compatible `/metrics` endpoint
inside the Compose network.

The exporter receives the existing `LANGFUSE_BASE_URL`,
`LANGFUSE_PUBLIC_KEY`, and `LANGFUSE_SECRET_KEY` values from
`apps/qanunai_backend/.env`; credentials are not embedded in the image or
Prometheus configuration. It exports a five-minute rolling window and polls
Langfuse every 60 seconds. Langfuse Metrics API v2 is supported by Langfuse
Cloud and self-hosted Langfuse v4+; self-hosted v3 requires the v1 API and is
not compatible with the default exporter query. The Compose configuration uses
a 24-hour rolling window so historical traces remain visible even when there
has been no traffic in the last few minutes.

The exporter provides aggregate observations, input/output tokens, average
latency, and cost. It intentionally does not export prompts, trace IDs, user
IDs, session IDs, or other high-cardinality data. Panels requiring cAdvisor,
DCGM, retrieved-document histograms, or custom evaluation instrumentation may
remain empty.
