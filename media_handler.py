import os
import shutil
from datetime import datetime
from typing import Dict, Optional
import logging
import re

from media_parser import sanitize_name

class MediaHandler:
    def __init__(self, config, logger: logging.Logger):
        self.logger = logger
        self.config = config

        # Enforce required config attributes
        if not hasattr(self.config, "duplicate_dir") or not self.config.duplicate_dir:
            self.logger.warning("Missing 'duplicate_dir' in config — defaulting to 'unknown_dir'")
            setattr(self.config, "duplicate_dir", self.config.unknown_dir)

    def construct_path(self, original_name: str, media_info: Dict[str, str], is_tv: bool) -> str:
        ext = os.path.splitext(original_name)[1].lower()

        if is_tv:
            show_name = sanitize_name(media_info.get("Title", original_name))
            season = media_info.get("season", "01")
            episode = media_info.get("episode", "01")
            end_episode = media_info.get("end_episode")
            ep_range = f"-E{end_episode}" if end_episode else ""
            filename = f"{show_name} S{season}E{episode}{ep_range}{ext}"

            path = os.path.join(
                self.config.tv_dir,
                show_name,
                f"Season {season}",
                filename
            )
            self.logger.debug(f"Constructed TV path: {path}")
            return path

        else:
            movie_title = sanitize_name(media_info.get("Title", original_name))
            year = media_info.get("Year", "0000")
            filename = f"{movie_title} ({year}){ext}"
            path = os.path.join(
                self.config.movies_dir,
                f"{movie_title} ({year})",
                filename
            )
            self.logger.debug(f"Constructed Movie path: {path}")
            return path

    def move_item(self, item_path: str, destination_dir: str, label: str):
        """Shared move logic for UNKNOWN and DUPLICATE handlers."""
        try:
            if not os.path.exists(item_path):
                self.logger.warning(f"File or folder does not exist, cannot move to {label.upper()}: {item_path}")
                return

            item_name = os.path.basename(item_path.rstrip("/"))
            base, ext = os.path.splitext(item_name)
            base = re.sub(r'(_\d{8}-\d{6})+', '', base)
            cleaned_name = sanitize_name(base)

            if os.path.isdir(item_path):
                cleaned_path = os.path.join(destination_dir, cleaned_name)
                target = cleaned_path
            else:
                cleaned_filename = f"{cleaned_name}{ext}"
                target = os.path.join(destination_dir, cleaned_filename)

            if os.path.exists(target):
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                if os.path.isdir(item_path):
                    target = f"{cleaned_path}_{timestamp}"
                else:
                    target = os.path.join(destination_dir, f"{cleaned_name}_{timestamp}{ext}")

            self.logger.debug(f"Moving {label.lower()} item from {item_path} to {target}")
            os.makedirs(destination_dir, exist_ok=True)
            shutil.move(item_path, target)
            self.logger.info(f"Moved to {label.upper()}: {target}")
        except Exception as e:
            self.logger.error(f"Failed to move to {label.upper()}: {str(e)}")

    def move_to_unknown(self, item_path: str):
        self.move_item(item_path, self.config.unknown_dir, "UNKNOWN")

    def move_to_duplicate(self, item_path: str):
        self.move_item(item_path, self.config.duplicate_dir, "DUPLICATE")

    def move_to_target(self, source_path: str, destination_path: str) -> Optional[str]:
        """Move file and return final destination path if moved."""
        if os.path.normpath(source_path) == os.path.normpath(destination_path):
            self.logger.debug("Source and destination are the same — skipping move.")
            return None

        if os.path.exists(destination_path):
            self.logger.warning(f"Destination already exists: {destination_path}")
            return None

        try:
            self.logger.debug(f"Moving file from {source_path} to {destination_path}")
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            shutil.move(source_path, destination_path)
            self.logger.info(f"Moved to: {destination_path}")
            return destination_path
        except Exception as e:
            self.logger.error(f"Error moving to target: {str(e)}")
            return None

    def write_sidecar_metadata(self, destination_path: str, metadata: Dict[str, str]):
        """Generate .json metadata next to the actual media file."""
        try:
            base_path = os.path.splitext(destination_path)[0]
            json_path = f"{base_path}.json"

            self.logger.debug(f"Writing sidecar metadata to {json_path}")
            with open(json_path, "w", encoding="utf-8") as f:
                import json
                json.dump(metadata, f, indent=2)

            self.logger.debug(f"Generated sidecar metadata at: {json_path}")
        except Exception as e:
            self.logger.warning(f"Failed to write sidecar metadata: {str(e)}")

