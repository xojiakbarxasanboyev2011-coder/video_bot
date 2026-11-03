"""
Cleaning up temporary files.

Deletes files in the `downloads/` folder that are older than a certain age.
This can be run as a background task in `bot/main.py`.
"""

import logging
import time
from pathlib import Path

from bot.config import DOWNLOAD_DIR

logger = logging.getLogger(__name__)

# Files older than 30 minutes will be cleaned up
MAX_AGE_SECONDS = 30 * 60


def cleanup_old_files() -> int:
    """
    Deletes old files in `DOWNLOAD_DIR`.

    Returns: the number of deleted files.
    """
    if not DOWNLOAD_DIR.exists():
        return 0

    now = time.time()
    removed = 0

    for file_path in DOWNLOAD_DIR.iterdir():
        if not file_path.is_file():
            continue
        try:
            age = now - file_path.stat().st_mtime
            if age > MAX_AGE_SECONDS:
                file_path.unlink()
                removed += 1
        except OSError as e:
            logger.warning("Failed to remove %s: %s", file_path, e)

    if removed:
        logger.info("Cleanup removed %d old file(s)", removed)
    return removed
