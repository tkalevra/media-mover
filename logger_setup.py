import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging(log_path: str, logger_name: str = "media_mover") -> logging.Logger:
    """Configure and return a logger with file and stream handlers."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers if reloaded
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File logging
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=5_000_000,
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Journalctl / stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

