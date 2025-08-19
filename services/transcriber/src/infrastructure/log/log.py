from logging import (
    getLogger,
    INFO, CRITICAL, DEBUG, ERROR, WARN,
    StreamHandler,
    Formatter,
    root
)
import sys

import structlog
from pydantic import Field
from pydantic_settings import BaseSettings

class LogConfig(BaseSettings):
    log_name: str = Field("name")
    log_level: str  = Field("info")
    disable_other_loggers: bool = Field(True)

    def get_log_level(self) -> int:
        match self.log_level:
            case "debug":
                return DEBUG
            case "info":
                return INFO
            case "warning":
                return WARN
            case "error":
                return ERROR
            case "fatal":
                return CRITICAL
            case _:
                raise ValueError("invalid log level specified")

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
