import time

from .registry import Metrics

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


class MetricsServerConfig(BaseSettings):
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=9090)


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
    async def handle_metrics(_: Request) -> StreamResponse:
        Metrics().update_uptime()
        return Response(body=generate_latest(), content_type="text/plain")

    async def start(self):
        self._runner = AppRunner(self.app)
        await self._runner.setup()
        self._site = TCPSite(self._runner, self.cfg.host, self.cfg.port)

        self.log.info(
            "starting metrics server",
            host=self.cfg.host,
            port=self.cfg.port
        )
        await self._site.start()
