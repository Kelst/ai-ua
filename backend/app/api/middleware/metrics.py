"""Prometheus metrics middleware."""
import time
import logging
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Define metrics
REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds",
    "API request latency",
    ["method", "endpoint"],
)

INFERENCE_LATENCY = Histogram(
    "inference_latency_seconds",
    "Model inference latency",
    ["model", "method"],
)

TOKENS_PER_SECOND = Gauge(
    "tokens_per_second",
    "Token generation rate",
)

ACTIVE_REQUESTS = Gauge(
    "active_requests",
    "Number of active requests",
)

MODEL_MEMORY_BYTES = Gauge(
    "model_memory_bytes",
    "Estimated model memory usage",
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics."""

    async def dispatch(self, request: Request, call_next):
        """Process request and collect metrics."""
        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        ACTIVE_REQUESTS.inc()
        start_time = time.time()

        try:
            response = await call_next(request)
            status = response.status_code
        except Exception as e:
            logger.error(f"Request error: {e}")
            status = 500
            raise
        finally:
            # Record metrics
            elapsed = time.time() - start_time
            ACTIVE_REQUESTS.dec()

            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=status,
            ).inc()

            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.url.path,
            ).observe(elapsed)

        return response


def get_metrics():
    """Return Prometheus metrics."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
