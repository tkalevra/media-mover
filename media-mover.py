#!/usr/bin/env python3

import time
import signal
import sys

from config_loader import load_config
from logger_setup import setup_logging
from omdb_client import OMDbClient
from media_handler import MediaHandler
from scanner import MediaScanner

shutdown_requested = False

def handle_shutdown(signum, frame):
    global shutdown_requested
    shutdown_requested = True
    print(f"\nReceived signal {signum}, shutting down gracefully...")

def main():
    global shutdown_requested

    try:
        # Load config
        config = load_config()

        # Set up logging
        logger = setup_logging(config.log_file)
        logger.info("Media Mover starting up...")

        # Register signals
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)

        # Init components
        omdb = OMDbClient(config.omdb_api_key, config.omdb_api_url, config.api_timeout, logger)
        handler = MediaHandler(config, logger)
        scanner = MediaScanner(config, logger, omdb, handler)
        scanner.set_shutdown_callback(lambda: shutdown_requested)

        # First run: scan UNKNOWN
        scanner.scan_unknown()

        # Main loop
        logger.info(f"Polling every {config.scan_interval}s")
        while not shutdown_requested:
            scanner.scan_uploads()
            for _ in range(config.scan_interval):
                if shutdown_requested:
                    break
                time.sleep(1)

        logger.info("Shutdown complete.")

    except Exception as e:
        print(f"Fatal error during startup: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

