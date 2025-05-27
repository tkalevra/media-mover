import time
import requests
from functools import lru_cache
from typing import Optional, Dict, Any
import logging

class OMDbClient:
    """Handles OMDb API querying with caching and logging."""

    def __init__(self, api_key: str, api_url: str, timeout: int = 10, logger: Optional[logging.Logger] = None):
        self.api_key = api_key
        self.api_url = api_url
        self.timeout = timeout
        self.api_call_count = 0
        self.last_reset = time.time()
        self.logger = logger or logging.getLogger("omdb_client")

    def reset_if_needed(self):
        if time.time() - self.last_reset > 86400:
            self.api_call_count = 0
            self.last_reset = time.time()

    @lru_cache(maxsize=500)
    def query(self, title: str, year: Optional[str] = None, media_type: str = "movie") -> Optional[Dict[str, Any]]:
        """Query OMDb and return JSON metadata or None."""
        self.reset_if_needed()

        if self.api_call_count >= 1000:
            self.logger.error("OMDb API rate limit reached (1000 calls/day)")
            return None

        params = {
            "apikey": self.api_key,
            "t": title,
            "type": media_type,
            "r": "json"
        }

        if year:
            params["y"] = year

        try:
            self.logger.info(f"Searching OMDb: '{title}' ({year}) [{media_type}]")
            start_time = time.time()

            response = requests.get(self.api_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            self.api_call_count += 1
            elapsed = time.time() - start_time
            data = response.json()

            if data.get("Response") == "True":
                self.logger.info(f"OMDb match: {data.get('Title')} ({data.get('Year')}) [in {elapsed:.2f}s]")
                return data

            self.logger.info(f"No OMDb match: {data.get('Error', 'Unknown error')} for '{title}'")
            return None

        except requests.RequestException as e:
            self.logger.warning(f"OMDb request failed: {str(e)}")
            return None

