# NOTE: This is a lightweight media_parser variant for media-dedupe.py only
# It is *not* a 1:1 copy of the main application's parser and may evolve separately

import re

def parse_title_year(filename):
    """
    Parses a basic title and optional year from a filename.
    Returns (title, year) tuple.
    """
    # Remove extension
    name = re.sub(r'\.[^.]+$', '', filename)

    # Remove common junk
    name = re.sub(r'\[.*?\]|\(.*?\)', '', name)
    name = re.sub(r'\b(1080p|720p|480p|x264|h264|bluray|web[-_. ]dl|webrip|dvdrip|aac|dts|yts|yify)\b', '', name, flags=re.IGNORECASE)

    # Try to extract year
    year_match = re.search(r'(19|20)\d{2}', name)
    year = year_match.group(0) if year_match else None

    # Remove year from name for title parsing
    if year:
        name = name.replace(year, '')

    # Clean leftover junk
    name = re.sub(r'[_\-]+', ' ', name)
    name = re.sub(r'\s{2,}', ' ', name)

    title = name.strip().title()
    return title, year

