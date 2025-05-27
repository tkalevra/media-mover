import os
import configparser
from dataclasses import dataclass
from typing import Optional, List

CONFIG_PATH = '/opt/media-mover/media-mover.conf'

@dataclass
class MediaMoverConfig:
    uploads_dir: str
    tv_dir: str
    movies_dir: str
    movies_kids_dir: str
    music_dir: str
    unknown_dir: str
    log_file: str
    scan_interval: int
    api_timeout: int
    use_inotify: bool
    omdb_api_key: str
    omdb_api_url: str

def load_config(path: str = CONFIG_PATH) -> MediaMoverConfig:
    """Load and validate configuration file into a structured config object."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Configuration file not found: {path}")

    parser = configparser.ConfigParser()
    parser.read(path)

    # Required keys
    api_key = parser.get('OMDb', 'api_key', fallback=None)
    if not api_key or api_key.strip().lower() == 'your_api_key':
        raise ValueError("OMDb API key is missing or default")

    def clean_int(val, fallback):
        return int(val.split('#')[0].strip()) if val else fallback

    config = MediaMoverConfig(
        uploads_dir = parser.get('Paths', 'uploads_dir'),
        tv_dir = parser.get('Paths', 'tv_dir'),
        movies_dir = parser.get('Paths', 'movies_dir'),
        movies_kids_dir = parser.get('Paths', 'movies_kids_dir'),
        music_dir = parser.get('Paths', 'music_dir'),
        unknown_dir = parser.get('Paths', 'unknown_dir'),
        log_file = parser.get('Paths', 'log_file'),
        scan_interval = clean_int(parser.get('Settings', 'scan_interval', fallback='300'), 300),
        api_timeout = parser.getint('Settings', 'api_timeout', fallback=10),
        use_inotify = parser.getboolean('Settings', 'use_inotify', fallback=False),
        omdb_api_key = api_key,
        omdb_api_url = parser.get('OMDb', 'api_url', fallback='http://www.omdbapi.com/')
    )

    # Auto-create all path directories
    for path in [
        config.uploads_dir, config.tv_dir, config.movies_dir,
        config.movies_kids_dir, config.music_dir, config.unknown_dir
    ]:
        os.makedirs(path, exist_ok=True)

    return config

