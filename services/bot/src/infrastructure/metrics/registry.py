import time

from prometheus_client import Histogram, Counter, Gauge


class Metrics:
    _instance: "Metrics"
    _start_time = time.time()
    _latency_buckets = [0.1, 0.5, 1.0, 1.5, 2.5, 5.0]

    def __new__(cls, *args, **kwargs) -> "Metrics":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.bot_requests_total = Counter("tg_bot_requests_total", "total bot requests")
        self.bot_errors_total = Counter("tg_bot_errors_total", "total bot errors")
        self.bot_latency = Histogram(
            "tg_bot_latency",
            "bot response latency",
            buckets=self._latency_buckets
        )

        self.kafka_consumed = Counter("tg_bot_kafka_consumed", "total amount of consumed messages")
        self.kafka_errors = Counter("tg_bot_kafka_errors", "total amount of kafka consumer errors")
        self.kafka_latency = Histogram(
            "tg_bot_kafka_latency",
            "kafka response latency",
            buckets=self._latency_buckets
        )

        self.uptime = Gauge("tg_bot_uptime", "bot instance uptime")

    def update_uptime(self):
        self.uptime.set(time.time() - self._start_time)
