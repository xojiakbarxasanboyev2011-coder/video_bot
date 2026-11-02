"""
Logging sozlamalari.

Butun loyiha uchun konsol va faylga yozadigan logger yaratadi.
`bot/main.py` da bir marta chaqiriladi.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(level: int = logging.INFO, log_file: str = "bot.log") -> None:
    """
    Root logger'ni sozlaydi.

    - Konsolga rangli (oddiy) formatda yozadi
    - `bot.log` fayliga aylanadigan (rotating) tarzda yozadi
      (10 MB dan oshsa, yangi fayl ochiladi, 3 ta zaxira saqlanadi)
    """
    root = logging.getLogger()
    root.setLevel(level)

    # Takroriy handler'larni oldini olish (reload paytida)
    if root.handlers:
        root.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1) Konsol
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    # 2) Fayl
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    # Aiogram va yt-dlp'ning ortiqcha DEBUG xabarlarini bostirish
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("yt_dlp").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
