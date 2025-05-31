import configparser
import os

CONFIG_PATH = "/opt/media-mover/media-mover.conf"

def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Config not found at {CONFIG_PATH}")
    
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config

