from time import perf_counter

from fastapi import FastAPI, Request
from prometheus_client import Counter, Gauge, Histogram, make_asgi_app

HTTP_REQUESTS = Counter(
    "rag_http_requests_total",
    "HTTP requests completed",
    ["method", "route", "status_code"],
)
HTTP_REQUEST_DURATION = Histogram(
    "rag_http_request_duration_seconds",
    "End-to-end HTTP request duration in seconds",
    ["method", "route"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60),
)
HTTP_IN_PROGRESS = Gauge(
    "rag_http_requests_in_progress",
    "HTTP requests currently being processed",
)
RETRIEVED_DOCUMENTS = Histogram(
    "rag_retrieved_documents",
    "Number of documents returned by retrieval per query",
    buckets=(0, 1, 2, 3, 4, 5, 8, 10, 15, 20, 30, 50),
)
RETRIEVAL_SIMILARITY = Histogram(
    "rag_retrieval_similarity",
    "Similarity scores returned by the retriever before threshold filtering",
    buckets=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
)
RETRIEVAL_QUERIES = Counter(
    "rag_retrieval_queries_total",
    "Retrieval queries observed by the application",
)
RETRIEVAL_CANDIDATES = Counter(
    "rag_retrieval_candidates_total",
    "Documents returned by the retriever before threshold filtering",
)
RETRIEVAL_ACCEPTED = Counter(
    "rag_retrieval_accepted_documents_total",
    "Documents remaining after score threshold filtering",
)
RETRIEVAL_EMPTY = Counter(
    "rag_retrieval_empty_queries_total",
    "Retrieval queries with no documents after threshold filtering",
)


def record_retrieved_documents(count: int) -> None:
    RETRIEVED_DOCUMENTS.observe(max(0, count))


def record_retrieval_quality(scores: list[float], accepted_count: int) -> None:
    RETRIEVAL_QUERIES.inc()
    RETRIEVAL_CANDIDATES.inc(len(scores))
    RETRIEVAL_ACCEPTED.inc(max(0, accepted_count))
    if accepted_count == 0:
        RETRIEVAL_EMPTY.inc()
    for score in scores:
        RETRIEVAL_SIMILARITY.observe(score)


def _route_name(request: Request) -> str:
    route = request.scope.get("route")
    return getattr(route, "path", request.url.path) if route else request.url.path


def install_metrics(app: FastAPI) -> None:
    """Install low-cardinality HTTP metrics and mount the Prometheus endpoint."""

    @app.middleware("http")
    async def prometheus_http_metrics(request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)

        start = perf_counter()
        status_code = 500
        HTTP_IN_PROGRESS.inc()
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            HTTP_REQUESTS.labels(
                request.method, _route_name(request), str(status_code)
            ).inc()
            HTTP_REQUEST_DURATION.labels(
                request.method, _route_name(request)
            ).observe(perf_counter() - start)
            HTTP_IN_PROGRESS.dec()

    app.mount("/metrics", make_asgi_app())
