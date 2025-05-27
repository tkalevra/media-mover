import re
from typing import Optional, Tuple, Dict
from unicodedata import normalize

def sanitize_name(text: str) -> str:
    """Convert to ASCII, remove special chars, and normalize spacing."""
    text = normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip()
    return re.sub(r'[._-]+', ' ', text).strip()

def parse_media_title(raw_name: str) -> Tuple[str, Optional[str]]:
    """Extract clean title and optional year from a raw filename."""
    try:
        clean_name = re.sub(
            r'\.(mkv|mp4|avi|mov|iso|zip|rar|r\d{1,3}|v\d{1,3})$', '', raw_name, flags=re.IGNORECASE
        )

        year_match = re.search(
            r'(?:^|\D)(\d{4})(?:\D|$)|\((\d{4})\)|\.(\d{4})\.', clean_name
        )
        year = next((y for y in year_match.groups() if y), None) if year_match else None

        title = re.sub(r'\(.*?\)|\[.*?\]|\d{3,4}p|\.\d{4}\.|[._-]+$', '', clean_name)
        title = re.sub(r'[._-]+', ' ', title).strip()

        return title, year
    except Exception:
        return raw_name, None

def is_tv_show(name: str) -> bool:
    """Detect typical TV episode patterns."""
    return bool(re.search(
        r'S\d{1,2}E\d{1,2}(?:-E?\d{1,2})?|Season[._ ]?\d{1,2}[._ ]?Episode[._ ]?\d{1,2}',
        name, re.IGNORECASE
    ))

def get_tv_show_info(name: str) -> Optional[Dict[str, str]]:
    """Extract season/episode from filename."""
    match = re.search(r'S(\d{1,2})E(\d{1,2})(?:-E?(\d{1,2}))?', name, re.IGNORECASE)
    if match:
        return {
            "season": match.group(1).zfill(2),
            "episode": match.group(2).zfill(2),
            "end_episode": match.group(3).zfill(2) if match.group(3) else None
        }
    return None

