import json

from app.redis_client import redis_client

STATS_CACHE_KEY = "stats:aggregate"
STATS_CACHE_TTL_SECONDS = 30


def get_cached_stats() -> dict | None:
    cached = redis_client.get(STATS_CACHE_KEY)
    if cached is None:
        return None
    return json.loads(cached)


def set_cached_stats(stats: dict) -> None:
    redis_client.setex(STATS_CACHE_KEY, STATS_CACHE_TTL_SECONDS, json.dumps(stats))


def invalidate_stats_cache() -> None:
    redis_client.delete(STATS_CACHE_KEY)
