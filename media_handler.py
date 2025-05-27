import os
import shutil
from datetime import datetime
from typing import Dict, Optional
import logging

from media_parser import sanitize_name

class MediaHandler:
    def __init__(self, config, logger: logging.Logger):
        self.config = config
        self.logger = logger

    def construct_path(self, original_name: str, media_info: Dict[str, str], is_tv: bool) -> str:
        ext = os.path.splitext(original_name)[1].lower()

        if is_tv:
            show_name = sanitize_name(media_info.get("Title", original_name))
            season = media_info.get("season", "01")
            episode = media_info.get("episode", "01")
            end_episode = media_info.get("end_episode")
            ep_range = f"-E{end_episode}" if end_episode else ""
            filename = f"{show_name} S{season}E{episode}{ep_range}{ext}"

            return os.path.join(
                self.config.tv_dir,
                show_name,
                f"Season {season}",
                filename
            )
        else:
            movie_title = sanitize_name(media_info.get("Title", original_name))
            year = media_info.get("Year", "0000")
            filename = f"{movie_title} ({year}){ext}"
            return os.path.join(
                self.config.movies_dir,
                f"{movie_title} ({year})",
                filename
            )

    def move_to_target(self, source_path: str, destination_path: str) -> Optional[str]:
        """Move file and return final destination path if moved."""
        if os.path.normpath(source_path) == os.path.normpath(destination_path):
            self.logger.debug("Source and destination are the same — skipping move.")
            return None

        if os.path.exists(destination_path):
            self.logger.warning(f"Destination already exists: {destination_path}")
            return None

        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        shutil.move(source_path, destination_path)
        self.logger.info(f"Moved to: {destination_path}")
        return destination_path

    def move_to_unknown(self, item_path: str):
        """Handle failed/unknown items by moving to unknown directory."""
        try:
            item_name = os.path.basename(item_path)
            target = os.path.join(self.config.unknown_dir, item_name)

            if os.path.exists(target):
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                base, ext = os.path.splitext(item_name)
                target = os.path.join(self.config.unknown_dir, f"{base}_{timestamp}{ext}")

            shutil.move(item_path, target)
            self.logger.info(f"Moved to UNKNOWN: {target}")
        except Exception as e:
            self.logger.error(f"Failed to move to UNKNOWN: {str(e)}")

    def write_sidecar_metadata(self, destination_path: str, metadata: Dict[str, str]):
        """Generate .json metadata next to the actual media file."""
        try:
            base_path = os.path.splitext(destination_path)[0]
            json_path = f"{base_path}.json"

            with open(json_path, "w", encoding="utf-8") as f:
                import json
                json.dump(metadata, f, indent=2)

            self.logger.debug(f"Generated sidecar metadata at: {json_path}")
        except Exception as e:
            self.logger.warning(f"Failed to write sidecar metadata: {str(e)}")

