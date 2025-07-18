import time

from prometheus_client import Histogram, Counter, Gauge

bot_requests_total = Counter("tg_bot_requests_total", "total bot requests")
bot_errors_total = Counter("tg_bot_errors_total", "total bot errors")
bot_latency = Histogram("tg_bot_latency", "bot response latency")

kafka_consumed = Counter("tg_bot_kafka_consumed", "total amount of consumed messages")
kafka_errors = Counter("tg_bot_kafka_errors", "total amount of kafka consumer errors")
kafka_latency = Histogram("tg_bot_kafka_latency", "kafka response latency")

uptime = Gauge("tg_bot_uptime", "bot instance uptime")
_start_time = time.time()
