import os

from redis import Redis
from rq import Queue, Worker


def main() -> None:
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        raise RuntimeError("REDIS_URL is required to start the queue worker")

    connection = Redis.from_url(redis_url)
    connection.ping()
    worker = Worker([Queue("seo_automation_queue", connection=connection)], connection=connection)
    worker.work()


if __name__ == "__main__":
    main()