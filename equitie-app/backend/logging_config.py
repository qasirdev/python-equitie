import logging
from typing import Any

import structlog

from .settings import settings


def setup_logging() -> Any:
    # Basic standard logging config to catch third party logs
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(message)s",
    )

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger("equitie_backend")


logger = setup_logging()
