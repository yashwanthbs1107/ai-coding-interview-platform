
import redis
from rq import Queue, SimpleWorker

# Separate binary-safe Redis connection for RQ
rq_redis = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=False,
    socket_connect_timeout=1,
    socket_timeout=1,
)

ai_queue = Queue(
    "ai-analysis",
    connection=rq_redis,
)

def start_worker():
    worker = SimpleWorker(
        [ai_queue],
        connection=rq_redis,
    )
    worker.work()

if __name__ == "__main__":
    start_worker()
