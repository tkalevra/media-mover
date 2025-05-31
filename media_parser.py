from guessit import guessit
from typing import Optional, Tuple, Dict
from unicodedata import normalize
import re

# --- Primary Regex for TV Episode Matching ---
TV_PATTERN = re.compile(
    r'(?P<title>.+?)[.\s_\-\[\(]*[Ss](?P<season>\d{1,2})[Ee](?P<episode>\d{2})(?:[-E]?(?P<end_episode>\d{2}))?[\]\).\s_\-]*',
    re.IGNORECASE
)

def sanitize_name(text: str) -> str:
    """Convert to ASCII, remove special chars, normalize spacing."""
    text = normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip()
    return re.sub(r'[._-]+', ' ', text).strip()

def parse_media_title(raw_name: str) -> Tuple[str, Optional[str]]:
    """Extract clean title and optional year using guessit."""
    try:
        guess = guessit(raw_name)
        title = guess.get('title')
        year = guess.get('year')
        return title, str(year) if year else None
    except Exception:
        return raw_name, None

def is_tv_show(name: str) -> bool:
    """Detect common TV show patterns in filename."""
    return bool(re.search(
        r'[Ss]\d{1,2}[Ee]\d{1,2}(?:[-E]?\d{1,2})?|Season[._ ]?\d{1,2}[._ ]?Episode[._ ]?\d{1,2}',
        name, re.IGNORECASE
    ))

def get_tv_show_info(name: str) -> Optional[Dict[str, str]]:
    """Extract season, episode, and optional range from filename."""
    match = TV_PATTERN.search(name)
    if match:
        return {
            "title": sanitize_name(match.group("title")),
            "season": match.group("season").zfill(2),
            "episode": match.group("episode").zfill(2),
            "end_episode": match.group("end_episode").zfill(2) if match.group("end_episode") else None
        }
    return None

