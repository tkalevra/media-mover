import os
import time
import shutil
import logging
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
        self._shutdown_callback = None

        log_level_str = getattr(self.config, "log_level", "INFO").upper()
        if log_level_str == "STDOUT":
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)
        else:
            log_level = getattr(logging, log_level_str, logging.INFO)
            self.logger.setLevel(log_level)

        self.logger.debug(f"Logger level set to: {log_level_str}")

        self.fuzzy_match_threshold = int(getattr(self.config, "fuzzy_match", 90))
        self.logger.debug(f"Fuzzy match threshold set to: {self.fuzzy_match_threshold}%")

        self.duplicate_dir = getattr(self.config, "duplicate_dir", os.path.join(self.config.uploads_dir, "DUPLICATE"))

    def set_shutdown_callback(self, callback: Callable[[], bool]):
        self._shutdown_callback = callback

    def should_shutdown(self):
        return callable(self._shutdown_callback) and self._shutdown_callback()

    def process_folder(self, folder_path: str):
        if folder_path.startswith(self.duplicate_dir):
            self.logger.debug(f"Skipping DUPLICATE folder: {folder_path}")
            return

        media_exts = (".mkv", ".mp4", ".avi", ".mov", ".flac", ".mp3")
        media_files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(media_exts)
        ]

        if not media_files:
            self.logger.warning(f"Folder has no media, moving to UNKNOWN: {folder_path}")
            self.handler.move_to_unknown(folder_path)
            return

        # Pick the largest media file as the representative
        main_media = max(media_files, key=os.path.getsize)
        self.process_file(main_media, parent_folder=folder_path)

    def process_file(self, path: str, parent_folder: str = None):
        if not os.path.exists(path):
            return

        media_exts = (".mkv", ".mp4", ".avi", ".mov", ".flac", ".mp3")
        if not path.lower().endswith(media_exts):
            self.logger.debug(f"Skipping non-media file: {path}")
            return

        item_name = os.path.basename(path)
        self.logger.info(f"Processing: {item_name}")
        self.logger.debug(f"Full path: {path}")

        try:
            title, year = parse_media_title(item_name)
            is_tv = is_tv_show(item_name)
            media_info = None

            if is_tv:
                tv_info = get_tv_show_info(item_name) or {}
                media_info = self.omdb.query(title, year, media_type="series") \
                              or self.omdb.fuzzy_search(title, media_type="series", threshold=self.fuzzy_match_threshold)
                if not media_info:
                    self.logger.warning(f"No OMDb match for series: {title}")
                    self.handler.move_to_unknown(parent_folder or path)
                    return
                media_info.update({
                    "Title": media_info.get("Title", title),
                    "season": tv_info.get("season", "01"),
                    "episode": tv_info.get("episode", "01"),
                    "end_episode": tv_info.get("end_episode")
                })
            else:
                media_info = self.omdb.query(title, year, media_type="movie") \
                              or self.omdb.fuzzy_search(title, media_type="movie", threshold=self.fuzzy_match_threshold)
                if not media_info:
                    self.logger.warning(f"No OMDb match for movie: {title}")
                    self.handler.move_to_unknown(parent_folder or path)
                    return
                media_info.update({
                    "Title": media_info.get("Title", title),
                    "Year": media_info.get("Year", year or "0000")
                })

            target_path = self.handler.construct_path(item_name, media_info, is_tv)
            if os.path.exists(target_path):
                self.logger.warning(f"Destination exists, moving to DUPLICATE: {target_path}")
                self.handler.move_to_duplicate(parent_folder or path)
                return

            final_path = self.handler.move_to_target(parent_folder or path, target_path)
            if final_path:
                self.handler.write_sidecar_metadata(final_path, media_info)

        except Exception as e:
            self.logger.error(f"Processing error: {str(e)}")
            self.handler.move_to_unknown(parent_folder or path)

        time.sleep(0.25)

    def scan_directory(self, path: str):
        if not os.path.exists(path):
            self.logger.warning(f"Path not found: {path}")
            return

        try:
            all_items = os.listdir(path)
            filtered_items = [
                os.path.join(path, item)
                for item in all_items
                if not item.startswith(".") and not any(x in item.lower() for x in ["partial", "@eadir", "unknown", "duplicate"])
            ]

            self.logger.info(f"Found {len(filtered_items)} items in {path}")
            for full_path in filtered_items:
                if self.should_shutdown():
                    self.logger.info("Shutdown requested — exiting scan loop.")
                    break

                if os.path.isdir(full_path):
                    self.logger.debug(f"Processing folder: {full_path}")
                    self.process_folder(full_path)
                elif os.path.isfile(full_path):
                    self.process_file(full_path)

        except Exception as e:
            self.logger.error(f"Scan failed: {str(e)}")

    def scan_uploads(self):
        self.logger.info("Scanning UPLOADS directory...")
        self.scan_directory(self.config.uploads_dir)

    def scan_unknown(self):
        self.logger.info("Re-scanning UNKNOWN directory...")
        self.scan_directory(self.config.unknown_dir)

