from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "path", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency", ["method", "path"]
)

TRIAGE_LATENCY = Histogram(
    "triage_latency_seconds", "Triage call latency"
)

TRIAGE_FALLBACK_COUNT = Counter(
    "triage_fallback_total", "Number of times triage fell back to rules"
)
