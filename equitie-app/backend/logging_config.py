import logging
from .settings import settings


def setup_logging():
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("equitie_backend")
    return logger


logger = setup_logging()
