import logging
import os

def setup_logger(name: str, log_file: str, level=logging.INFO, console_output=False):
    """
    Set up and return a logger instance.
    - name: logger name
    - log_file: file path for persistent log
    - level: logging level
    - console_output: if True, also log to stdout
    """
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    if console_output:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger

