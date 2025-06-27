import logging

from riskgpt.logger import configure_logging, logger


def test_configure_logging_adds_handler():
    logger.handlers.clear()
    configure_logging(level=logging.DEBUG)
    assert logger.level == logging.DEBUG
    assert logger.handlers
