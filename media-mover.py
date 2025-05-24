import os
import shutil
import logging
import configparser
import requests
import sys

# Load Configuration
config = configparser.ConfigParser()
config.read('/opt/media-mover/media-mover.conf')

UPLOADS_DIR = config.get('Paths', 'uploads_dir')
LOG_FILE = config.get('Paths', 'log_file')
TV_DIR = config.get('Paths', 'tv_dir')
MOVIES_DIR = config.get('Paths', 'movies_dir')
MOVIES_KIDS_DIR = config.get('Paths', 'movies_kids_dir')
MUSIC_DIR = config.get('Paths', 'music_dir')
UNKNOWN_DIR = config.get('Paths', 'unknown_dir')
OMDB_API_KEY = config.get('OMDb', 'api_key')
OMDB_API_URL = config.get('OMDb', 'api_url')

# Logging Configuration (file + journal)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(stream_handler)

def is_tv_show(name):
    return "S" in name and "E" in name

def is_movie(name):
    return name.lower().endswith(('.mkv', '.mp4', '.avi', '.mov'))

def classify_and_move(item_path):
    item_name = os.path.basename(item_path)

    if os.path.isdir(item_path):
        if is_tv_show(item_name):
            destination = os.path.join(TV_DIR, item_name)
        elif is_movie(item_name):
            destination = os.path.join(MOVIES_DIR, item_name)
        else:
            destination = os.path.join(UNKNOWN_DIR, item_name)

        try:
            if not os.path.exists(destination):
                shutil.move(item_path, destination)
                logging.info(f"Moved directory: {item_path} -> {destination}")
            else:
                logging.info(f"Skipped (already exists): {item_path}")
        except Exception as e:
            logging.error(f"Failed to move directory: {item_path} -> {destination} - Error: {str(e)}")

    elif os.path.isfile(item_path):
        logging.info(f"Skipped file (not a directory): {item_path}")

def main():
    logging.info("Media Mover started.")
    if not os.path.exists(UPLOADS_DIR):
        logging.error(f"Uploads directory does not exist: {UPLOADS_DIR}")
        return

    ignored_dirs = {'partial', 'UNKNOWN'}
    for item in os.listdir(UPLOADS_DIR):
        if item in ignored_dirs:
            logging.info(f"Ignored directory: {item}")
            continue
        item_path = os.path.join(UPLOADS_DIR, item)
        classify_and_move(item_path)

if __name__ == "__main__":
    main()

