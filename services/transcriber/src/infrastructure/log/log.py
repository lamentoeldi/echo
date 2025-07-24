from logging import (
    getLogger,
    INFO, CRITICAL,
    StreamHandler,
    Formatter,
    root
)
import sys

import structlog


def setup_logger(
    name: str = "main",
    level: int = INFO,
    disable_other_loggers: bool = True
) -> structlog.BoundLogger:
    logger = getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    handler = StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(Formatter("%(message)s"))
    logger.handlers = [handler]

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )

    if disable_other_loggers:
        for other_name in root.manager.loggerDict:
            if not other_name.startswith(name):
                other_logger = getLogger(other_name)
                other_logger.setLevel(CRITICAL + 1)
                other_logger.propagate = False

    return structlog.get_logger(name)
