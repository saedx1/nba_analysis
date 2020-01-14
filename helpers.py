"""
This module contains a set of helping functions to be used in other modules.
"""
import logging


def get_logger(name: str = "nba_analysis"):
    logger = logging.getLogger(name)
    return logger
