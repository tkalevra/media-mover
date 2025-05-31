import os
import json
import argparse
import logging
from logger_setup import setup_logger, load_config
from media_parser_dedupe import parse_title_year
import xxhash
from pathlib import Path
from collections import defaultdict

# Argument Parsing
parser = argparse.ArgumentParser(description="Media Dedupe Finder")
parser.add_argument('-d', '--dirs', help='Comma-separated list of directories to scan')
parser.add_argument('-n', '--normalize', action='store_true', help='Use normalized API-based title matching')
parser.add_argument('-j', '--json', action='store_true', help='Output results in JSON format')
parser.add_argument('-l', '--log', action='store_true', help='Log results to a file in /var/log/media-dedupe.log')
parser.add_argument('-o', '--output', help='Override output file path')
parser.add_argument('-i', '--interactive', action='store_true', help='Interactive preview mode (not implemented)')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose debug logging')
args = parser.parse_args()

# Load config and logger
config = load_config()
media_dirs = args.dirs.split(',') if args.dirs else [
    config.get('Paths', 'tv_dir'),
    config.get('Paths', 'movies_dir'),
    config.get('Paths', 'movies_kids_dir'),
    config.get('Paths', 'music_dir')
]
logger = setup_logger(level=logging.DEBUG if args.verbose else logging.INFO)

# Hashing
def hash_file(file_path):
    h = xxhash.xxh64()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        logger.warning(f"Failed to hash {file_path}: {e}")
        return None

# Deduplication scanning
def scan_files(base_dirs):
    seen = defaultdict(list)
    for base in base_dirs:
        for root, _, files in os.walk(base):
            for f in files:
                full_path = os.path.join(root, f)
                file_hash = hash_file(full_path)
                if file_hash:
                    seen[file_hash].append(full_path)
    return {k: v for k, v in seen.items() if len(v) > 1}

# Main logic
logger.info("Starting media deduplication scan...")
duplicates = scan_files(media_dirs)

if args.json:
    output_data = json.dumps(duplicates, indent=2)
else:
    output_data = "\n".join([
        f"Hash: {k}\n" + "\n".join([f"  - {f}" for f in v])
        for k, v in duplicates.items()
    ])

if args.output:
    out_path = Path(args.output)
else:
    out_path = Path.cwd() / 'media-dedupe-results.json' if args.json else Path.cwd() / 'media-dedupe-results.txt'

out_path.write_text(output_data)
if args.log:
    logger.info(f"Wrote deduplication results to {out_path}")

if args.interactive:
    print("[INTERACTIVE MODE NOT IMPLEMENTED]")

logger.info("Media deduplication scan complete.")

