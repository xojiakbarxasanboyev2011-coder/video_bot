"""
Utils paketi.

Yordamchi funksiyalar va modullar:
- validators: URL ajratish, platformani aniqlash
- logger: logging sozlamalari

Foydalanish:
    from bot.utils import extract_url, is_supported_url
    from bot.utils import setup_logging
"""

from .validators import (
    extract_url,
    is_supported_url,
    detect_platform,
)
from .logger import setup_logging

__all__ = [
    "extract_url",
    "is_supported_url",
    "detect_platform",
    "setup_logging",
]
