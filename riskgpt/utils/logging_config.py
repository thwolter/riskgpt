import logging
import os

DEFAULT_LEVEL = os.getenv("RISKGPT_LOG_LEVEL", "INFO").upper()
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def configure_logging(level: str | None = None, fmt: str | None = None) -> None:
    """Configure package-wide logging.

    Parameters
    ----------
    level: str | None
        Logging level as string. Defaults to environment variable
        ``RISKGPT_LOG_LEVEL`` or ``INFO``.
    fmt: str | None
        Logging format string. Defaults to a basic format including time,
        logger name, level and message.
    """
    logging.basicConfig(level=(level or DEFAULT_LEVEL), format=(fmt or DEFAULT_FORMAT))

