import logging

from src import configure_logging
from src import logger


def test_configure_logging_adds_handler():
    logger.handlers.clear()
    configure_logging(level=logging.DEBUG)
    assert logger.level == logging.DEBUG
    assert logger.handlers
