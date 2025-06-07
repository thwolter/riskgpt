import logging

from riskgpt.logger import logger, configure_logging


def test_configure_logging_adds_handler():
    logger.handlers.clear()
    configure_logging(level=logging.DEBUG)
    assert logger.level == logging.DEBUG
    assert logger.handlers

