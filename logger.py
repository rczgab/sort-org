# logger.py

import logging
import os
from logging.handlers import RotatingFileHandler
import config as c
class MaxLevelFilter(logging.Filter):
    """Filters (lets through) all messages with level <= LEVEL"""
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno <= self.level

def global_logging(output_main):
    info_log_path = os.path.normpath(os.path.join(output_main, 'info.log'))
    error_log_path = os.path.normpath(os.path.join(output_main, 'error.log'))

    # Create the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all levels of logs

    # Define formatters
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Create handlers
    info_handler = RotatingFileHandler(
        info_log_path, maxBytes=15 * 1024 * 1024, backupCount=100, encoding='utf-8'
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    info_handler.addFilter(MaxLevelFilter(logging.INFO))  # Only log up to INFO level

    error_handler = RotatingFileHandler(
        error_log_path, maxBytes=15 * 1024 * 1024, backupCount=100, encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
