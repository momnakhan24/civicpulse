import hashlib
import json

from app.redis_client import redis_client
from app.providers.triage.base import TriageResult

TRIAGE_CACHE_TTL_SECONDS = 24 * 60 * 60
HIT_COUNTER_KEY = "triage_cache:hits"
MISS_COUNTER_KEY = "triage_cache:misses"


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.strip().lower().encode()).hexdigest()


def get_cached_triage(text: str) -> TriageResult | None:
    key = f"triage_cache:{_content_hash(text)}"
    cached = redis_client.get(key)

    if cached is None:
        redis_client.incr(MISS_COUNTER_KEY)
        return None

    redis_client.incr(HIT_COUNTER_KEY)
    data = json.loads(cached)
    return TriageResult(**data)


def set_cached_triage(text: str, result: TriageResult) -> None:
    key = f"triage_cache:{_content_hash(text)}"
    redis_client.setex(key, TRIAGE_CACHE_TTL_SECONDS, result.model_dump_json())


def get_cache_hit_rate() -> float:
    hits = int(redis_client.get(HIT_COUNTER_KEY) or 0)
    misses = int(redis_client.get(MISS_COUNTER_KEY) or 0)
    total = hits + misses
    if total == 0:
        return 0.0
    return round(hits / total, 3)
