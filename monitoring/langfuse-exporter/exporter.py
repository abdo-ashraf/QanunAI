import base64
import json
import logging
import os
import threading
import time
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Gauge
from prometheus_client import generate_latest

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("langfuse-exporter")

HOST = os.getenv("LANGFUSE_BASE_URL", os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")).rstrip("/")
PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
POLL_INTERVAL = max(15, int(os.getenv("LANGFUSE_METRICS_INTERVAL_SECONDS", "60")))
WINDOW_SECONDS = max(60, int(os.getenv("LANGFUSE_METRICS_WINDOW_SECONDS", "300")))
LISTEN_PORT = int(os.getenv("PORT", "9800"))

registry = CollectorRegistry()
exporter_up = Gauge(
    "langfuse_metrics_exporter_up",
    "Whether the last Langfuse Metrics API request succeeded",
    registry=registry,
)
observations = Gauge(
    "langfuse_observations_window_total",
    "Langfuse observations in the configured rolling window",
    ["window"],
    registry=registry,
)
input_tokens = Gauge(
    "langfuse_input_tokens_window_total",
    "Langfuse input tokens in the configured rolling window",
    ["window"],
    registry=registry,
)
output_tokens = Gauge(
    "langfuse_output_tokens_window_total",
    "Langfuse output tokens in the configured rolling window",
    ["window"],
    registry=registry,
)
average_latency = Gauge(
    "langfuse_average_latency_milliseconds",
    "Average Langfuse observation latency in the configured rolling window",
    ["window"],
    registry=registry,
)
total_cost = Gauge(
    "langfuse_total_cost_window",
    "Langfuse total cost in the configured rolling window",
    ["window"],
    registry=registry,
)
last_success = Gauge(
    "langfuse_metrics_last_success_timestamp_seconds",
    "Unix timestamp of the last successful Langfuse Metrics API request",
    registry=registry,
)


def _number(row: dict[str, object], key: str) -> float:
    value = row.get(key, 0)
    return float(value) if value is not None else 0.0


def _query() -> dict[str, object]:
    now = datetime.now(timezone.utc)
    start = now - timedelta(seconds=WINDOW_SECONDS)
    query = {
        "view": "observations",
        "metrics": [
            {"measure": "inputTokens", "aggregation": "sum"},
            {"measure": "outputTokens", "aggregation": "sum"},
            {"measure": "latency", "aggregation": "avg"},
            {"measure": "totalCost", "aggregation": "sum"},
            {"measure": "count", "aggregation": "sum"},
        ],
        "dimensions": [],
        "filters": [],
        "fromTimestamp": start.isoformat().replace("+00:00", "Z"),
        "toTimestamp": now.isoformat().replace("+00:00", "Z"),
        "config": {"row_limit": 1},
    }
    encoded = urlencode({"query": json.dumps(query, separators=(",", ":"))})
    request = Request(
        f"{HOST}/api/public/v2/metrics?{encoded}",
        headers={
            "Accept": "application/json",
            "Authorization": "Basic "
            + base64.b64encode(f"{PUBLIC_KEY}:{SECRET_KEY}".encode()).decode(),
        },
    )
    with urlopen(request, timeout=15) as response:
        return json.load(response)


def collect() -> None:
    if not PUBLIC_KEY or not SECRET_KEY:
        raise RuntimeError("LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY are required")

    payload = _query()
    rows = payload.get("data", [])
    row = rows[0] if isinstance(rows, list) and rows else {}
    if not isinstance(row, dict):
        raise RuntimeError("Langfuse Metrics API returned an invalid data row")

    window = str(WINDOW_SECONDS)
    observations.labels(window).set(_number(row, "sum_count"))
    input_tokens.labels(window).set(_number(row, "sum_inputTokens"))
    output_tokens.labels(window).set(_number(row, "sum_outputTokens"))
    average_latency.labels(window).set(_number(row, "avg_latency"))
    total_cost.labels(window).set(_number(row, "sum_totalCost"))
    exporter_up.set(1)
    last_success.set(time.time())


def poll() -> None:
    while True:
        try:
            collect()
        except Exception:
            exporter_up.set(0)
            logger.exception("Langfuse Metrics API collection failed")
        time.sleep(POLL_INTERVAL)


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/-/ready":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ready\n")
            return
        if self.path != "/metrics":
            self.send_error(404)
            return
        body = generate_latest(registry)
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPE_LATEST)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args: object) -> None:
        return


if __name__ == "__main__":
    threading.Thread(target=poll, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", LISTEN_PORT), MetricsHandler).serve_forever()
