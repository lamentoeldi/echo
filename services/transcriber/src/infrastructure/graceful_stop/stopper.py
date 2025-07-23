import asyncio
from typing import Callable, Awaitable, Union, List

from structlog.stdlib import BoundLogger

ShutdownCallback = Union[Callable[[], Awaitable[None]], Callable[[], None]]


class GracefulStopper:
    """
    Runs graceful stop callbacks on signals.
    """
    def __init__(
        self,
        log: BoundLogger,
        callbacks: List[ShutdownCallback],
        signals: List[int],
        stop_timeout: int = 10,
    ):
        self._log = log
        self._signals = signals
        self._callbacks = callbacks
        self._stop_event = asyncio.Event()
        self._stop_timeout = stop_timeout

    def add_callback(self, cb: ShutdownCallback):
        self._callbacks.append(cb)

    def _signal_handler(self):
        self._log.info("received stop signal")
        self._stop_event.set()

    async def run(self):
        loop = asyncio.get_running_loop()
        for sig in self._signals:
            loop.add_signal_handler(sig, self._signal_handler)

        await self._stop_event.wait()
        self._log.info("graceful stopping")

        timeout = self._stop_timeout//len(self._callbacks)

        for cb in self._callbacks:
            res = cb()
            if asyncio.iscoroutine(res):
                try:
                    await asyncio.wait_for(res, timeout=timeout)
                except asyncio.TimeoutError:
                    self._log.info(f"failed graceful stop on {res.__name__} because of timeout")

        self._log.info("graceful stop complete")
