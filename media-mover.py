import os
import re
import requests
import logging
import shutil
import sys
import configparser

# Load configuration
CONFIG_FILE = '/opt/media-mover/media-mover.conf'
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# Configuration
UPLOADS_DIR = config.get('Paths', 'uploads_dir', fallback='/mnt/uploads')
LOG_FILE = config.get('Paths', 'log_file', fallback='/var/log/media-mover.log')
OMDB_API_KEY = config.get('OMDb', 'api_key', fallback='4b7c2635')
OMDB_API_URL = config.get('OMDb', 'api_url', fallback='http://www.omdbapi.com/')

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Regex patterns for media identification
TV_PATTERN = re.compile(r'(S\d{2}E\d{2}|Season \d+)', re.IGNORECASE)
MOVIE_PATTERN = re.compile(r'\.(mkv|mp4|avi|mov)$', re.IGNORECASE)
MUSIC_PATTERN = re.compile(r'\.(mp3|flac|wav)$', re.IGNORECASE)

# Target directories
DEST_DIRS = {
    'TV': config.get('Paths', 'tv_dir'),
    'MOVIES': config.get('Paths', 'movies_dir'),
    'MOVIES-KIDS': config.get('Paths', 'movies_kids_dir'),
    'MUSIC': config.get('Paths', 'music_dir'),
    'UNKNOWN': config.get('Paths', 'unknown_dir')
}

# Ensure required directories exist
for key, path in DEST_DIRS.items():
    if key in ['TV', 'MOVIES', 'MOVIES-KIDS', 'MUSIC']:
        if not os.path.exists(path):
            logging.error(f"Critical Error: Directory {path} does not exist. Exiting.")
            sys.exit(1)
    else:
        os.makedirs(path, exist_ok=True)

# Dry-run flag
DRY_RUN = '--dry-run' in sys.argv

# Function to query OMDb API for media details
def query_omdb(title):
    try:
        response = requests.get(OMDB_API_URL, params={'t': title, 'apikey': OMDB_API_KEY})
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logging.error(f"OMDb API Error: {str(e)}")
    return None

# Function to classify media and format names
def classify_media(file_name):
    if TV_PATTERN.search(file_name):
        return 'TV'
    elif MUSIC_PATTERN.search(file_name):
        return 'MUSIC'
    elif MOVIE_PATTERN.search(file_name):
        return 'MOVIES'
    return 'UNKNOWN'

# Function to move and rename files
def move_and_rename(file_path, category):
    file_name = os.path.basename(file_path)
    new_name = file_name.replace(' ', '.').replace('1080p', '1080p').replace('720p', '720p')

    if category in DEST_DIRS:
        new_path = os.path.join(DEST_DIRS[category], new_name)
    else:
        new_path = os.path.join(DEST_DIRS['UNKNOWN'], new_name)

    if DRY_RUN:
        logging.info(f"[DRY-RUN] Would move: {file_path} -> {new_path}")
        return

    if not os.path.exists(new_path):
        shutil.move(file_path, new_path)
        logging.info(f"Moved: {file_path} -> {new_path}")
    else:
        logging.warning(f"Skipped (exists): {new_path}")

# Main function
def scan_uploads():
    for root, dirs, files in os.walk(UPLOADS_DIR):
        # Exclude UNKNOWN directory
        dirs[:] = [d for d in dirs if d != 'UNKNOWN']
        for file in files:
            file_path = os.path.join(root, file)
            category = classify_media(file)
            move_and_rename(file_path, category)

if __name__ == '__main__':
    scan_uploads()

