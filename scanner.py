import os
import time
from typing import Callable

from media_parser import (
    parse_media_title,
    is_tv_show,
    get_tv_show_info
)

class MediaScanner:
    def __init__(self, config, logger, omdb, handler):
        self.config = config
        self.logger = logger
        self.omdb = omdb
        self.handler = handler
        self.shutdown_requested = False

    def set_shutdown_callback(self, callback: Callable[[], bool]):
        """Pass in a callable that returns True if shutdown was requested."""
        self.shutdown_requested = callback

    def process_file(self, path: str):
        if not os.path.exists(path):
            return

		media_exts = (".mkv", ".mp4", ".avi", ".mov", ".flac", ".mp3")
		non_media_exts = (".json", ".nfo", ".txt", ".jpg", ".png")

		# skip obvious non-media
		if not path.lower().endswith(media_exts):
			self.logger.debug(f"Skipping non-media file: {path}")
			return

        item_name = os.path.basename(path)
        self.logger.info(f"Processing: {item_name}")
        self.logger.debug(f"Full path: {path}")

        try:
            title, year = parse_media_title(item_name)
            self.logger.debug(f"Parsed: {title} | Year: {year}")
            is_tv = is_tv_show(item_name)

            if is_tv:
                tv_info = get_tv_show_info(item_name) or {}
                media_info = self.omdb.query(title, year, media_type="series") or {
                    "Title": title,
                    "season": tv_info.get("season", "01"),
                    "episode": tv_info.get("episode", "01"),
                    "end_episode": tv_info.get("end_episode")
                }
            else:
                media_info = self.omdb.query(title, year, media_type="movie") or {
                    "Title": title,
                    "Year": year or "0000"
                }

            target_path = self.handler.construct_path(item_name, media_info, is_tv)

            # ✅ Move and only write sidecar if move was successful
            final_path = self.handler.move_to_target(path, target_path)
            if final_path:
                self.handler.write_sidecar_metadata(final_path, media_info)

        except Exception as e:
            self.logger.error(f"Processing error: {str(e)}")
            self.handler.move_to_unknown(path)

    def scan_directory(self, path: str):
        if not os.path.exists(path):
            self.logger.warning(f"Path not found: {path}")
            return

        try:
            all_items = os.listdir(path)
            filtered_items = [
                os.path.join(path, item)
                for item in all_items
                if not item.startswith(".") and not any(x in item.lower() for x in ["partial", "@eadir"])
            ]

            self.logger.info(f"Found {len(filtered_items)} items in {path}")
            for full_path in filtered_items:
                if self.shutdown_requested and self.shutdown_requested():
                    break
                self.process_file(full_path)

        except Exception as e:
            self.logger.error(f"Scan failed: {str(e)}")

    def scan_uploads(self):
        self.logger.info("Scanning UPLOADS directory...")
        self.scan_directory(self.config.uploads_dir)

    def scan_unknown(self):
        self.logger.info("Re-scanning UNKNOWN directory...")
        self.scan_directory(self.config.unknown_dir)

