import configparser
import logging
import os

CONFIG_PATH = "/opt/media-mover/media-mover.conf"

def load_config():
    """
    Load and return configuration from CONFIG_PATH.
    Note: This module is intended for use in multiple tools.
    """
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config not found at {CONFIG_PATH}")

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config

def setup_logger(name='media_dedupe', log_file='/var/log/media-dedupe.log', level=logging.INFO, console_output=True):
    """
    Set up a logger with the given name and parameters.
    - name: Name of the logger.
    - log_file: Path to the log file.
    - level: Logging level.
    - console_output: If True, also logs to console.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # File handler
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console handler
    if console_output:
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger

