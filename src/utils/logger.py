"""
logger.py module.

This module provides logging functionality for the Time Tracker Console
Application.
"""

import logging


def custom_logger(module_name="time_tracker_app"):
    """Create logger instance and log data with respective module names.

    Args:
        module_name (str, optional): Module name to be used as logger name.
        Defaults to "time_tracker_app".

    Returns:
        logging.Logger: Logger instance.
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("src/utils/logs.log")

    console_handler.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.INFO)

    console_format = logging.Formatter(
        "%(name)s - %(levelname)s - %(message)s"
    )
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


if __name__ == "__main__":
    custom_logger(__name__)
