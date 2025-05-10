# Media Mover

## Overview
Media Mover is an automated Python script that scans a specified upload directory for media files (TV shows, Movies, Music) and organizes them into their respective folders. It supports TV, Movies, Kids Movies, Music, and an "Unknown" category for unrecognized files.

## Features
- Automatically detects and categorizes media files based on filename patterns and extensions.
- Supports TV shows, Movies, Kids Movies, and Music.
- Uses the OMDb API to enhance movie detection and categorization.
- Configurable using a clean configuration file (`media-mover.conf`).
- Supports a "dry-run" mode to simulate file moves without making changes.
- Systemd service and timer integration for automated runs.

## Installation
1. Clone the repo to your desired location:
   ```bash
   git clone https://your-git-repo-url.git /opt/media-mover
   ```
2. Create the Python virtual environment:
   ```bash
   cd /opt/media-mover
   python3 -m venv media-mover-venv
   source media-mover-venv/bin/activate
   pip install -r requirements.txt
   ```
3. Adjust the configuration file (`/opt/media-mover/media-mover.conf`) to match your directory structure.

## Configuration
Edit `/opt/media-mover/media-mover.conf` to set your paths:
```ini
[Paths]
uploads_dir = /mnt/uploads
log_file = /var/log/media-mover.log
tv_dir = /mnt/MEDIA/TV/
movies_dir = /mnt/MEDIA/MOVIES/
movies_kids_dir = /mnt/MOVIES-KIDS/
music_dir = /mnt/MUSIC/
unknown_dir = /mnt/MEDIA/uploads/UNKNOWN/

[OMDb]
api_key = YOUR_API_KEY
api_url = http://www.omdbapi.com/
```

## Usage
- Run in "dry-run" mode:
  ```bash
  python3 /opt/media-mover/media-mover.py --dry-run
  ```
- Run normally (moves files):
  ```bash
  python3 /opt/media-mover/media-mover.py
  ```

## Systemd Setup
1. Copy the service and timer files to `/etc/systemd/system/`:
   ```bash
   cp /opt/media-mover/systemd/media-mover.service /etc/systemd/system/
   cp /opt/media-mover/systemd/media-mover.timer /etc/systemd/system/
   ```
2. Enable and start the timer:
   ```bash
   systemctl daemon-reload
   systemctl enable media-mover.timer
   systemctl start media-mover.timer
   ```

## Logs
- Logs are saved to the specified log file (default: `/var/log/media-mover.log`).

## License
This project is licensed under the MIT License.

