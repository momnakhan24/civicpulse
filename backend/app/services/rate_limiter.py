from app.redis_client import redis_client
from app.config import settings

WINDOW_SECONDS = 60


def is_rate_limited(client_ip: str) -> tuple[bool, int]:
    key = f"ratelimit:{client_ip}"
    current = redis_client.incr(key)

    if current == 1:
        redis_client.expire(key, WINDOW_SECONDS)

    if current > settings.rate_limit_per_minute:
        ttl = redis_client.ttl(key)
        return True, max(ttl, 1)

    return False, 0
