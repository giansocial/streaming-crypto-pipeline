import logging
import os


def get_logger(name):
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)

    logger.setLevel(getattr(logging, level, logging.INFO))
    return logger
