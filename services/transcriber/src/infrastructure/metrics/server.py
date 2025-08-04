from time import time

from aiohttp.web import (
    Application,
    Request,
    StreamResponse,
    Response,
    AppRunner,
    TCPSite,
    middleware
)
from pydantic import Field
from pydantic_settings import BaseSettings
from prometheus_client import generate_latest
from structlog.stdlib import BoundLogger
from prometheus_client import Gauge

_start_time = time()

uptime = Gauge(
    "tg_bot_uptime",
    "bot instance uptime",
)


class MetricsServerConfig(BaseSettings):
    metrics_host: str = Field(default="0.0.0.0")
    metrics_port: int = Field(default=9090)


class MetricsServer:
    cfg: MetricsServerConfig
    app: Application
    _runner: AppRunner
    _site: TCPSite

    def __init__(self, cfg: MetricsServerConfig, log: BoundLogger):
        self.app = Application(middlewares=[
            self._mw_error_handler()
        ])
        self.cfg = cfg
        self.log = log

        self.app.router.add_get("/health", self.handle_healthcheck)
        self.app.router.add_get("/metrics", self.handle_metrics)

    def _mw_error_handler(self):
        @middleware
        async def mw(req: Request, handler) -> StreamResponse:
            try:
                return await handler(req)
            except Exception as err:
                self.log.error(str(err))
                return Response(status=500)
        return mw

    @staticmethod
    async def handle_healthcheck(_: Request) -> StreamResponse:
        return Response(status=200)

    @staticmethod
    async def handle_metrics(_: Request) -> StreamResponse:
        uptime.set(time() - _start_time)
        metrics = generate_latest()
        return Response(body=metrics, content_type="text/plain")

    async def start(self):
        self._runner = AppRunner(self.app)
        await self._runner.setup()
        self._site = TCPSite(self._runner, self.cfg.metrics_host, self.cfg.metrics_port)

        self.log.info(
            "starting metrics server",
            host=self.cfg.metrics_host,
            port=self.cfg.metrics_port
        )
        await self._site.start()

    async def stop(self):
        await self._site.stop()
        await self._runner.shutdown()
        await self._runner.cleanup()
