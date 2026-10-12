
import redis
from redis.retry import Retry
from redis.backoff import NoBackoff

redis_client = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1,
    retry=Retry(NoBackoff(), retries=0)
)
