import logging


def get_logger(name: str = "nba_analysis"):
    logger = logging.getLogger(name)
    return logger
