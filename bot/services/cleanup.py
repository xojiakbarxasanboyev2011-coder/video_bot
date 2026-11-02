"""
Vaqtinchalik fayllarni tozalash.

`downloads/` papkasidagi ma'lum vaqtdan eski fayllarni o'chiradi.
Bu `bot/main.py` da davriy vazifa (background task) sifatida
ishga tushirilishi mumkin.
"""

import logging
import time
from pathlib import Path

from bot.config import DOWNLOAD_DIR

logger = logging.getLogger(__name__)

# 30 daqiqadan eski fayllar tozalanadi
MAX_AGE_SECONDS = 30 * 60


def cleanup_old_files() -> int:
    """
    `DOWNLOAD_DIR` dagi eski fayllarni o'chiradi.

    Qaytaradi: o'chirilgan fayllar soni.
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
