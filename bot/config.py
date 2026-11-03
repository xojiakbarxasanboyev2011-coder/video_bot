"""
Loyiha sozlamalari.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# ─────────────────────────────────────────────────────────────
# Yordamchi funksiyalar
# ─────────────────────────────────────────────────────────────

def _get_env(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            raise RuntimeError(f"'{name}' muhit o'zgaruvchisi topilmadi.")
        return default or ""
    return value.strip()


def _get_int(name: str, default: int = 0) -> int:
    raw = _get_env(name, default=str(default))
    try:
        return int(raw)
    except ValueError:
        return default


def _get_bool(name: str, default: bool = False) -> bool:
    raw = _get_env(name, default="true" if default else "false").lower()
    return raw in ("1", "true", "yes", "on")


# ─────────────────────────────────────────────────────────────
# Bot sozlamalari
# ─────────────────────────────────────────────────────────────

BOT_TOKEN: str = _get_env("BOT_TOKEN", required=True)

ADMIN_IDS: list[int] = [
    int(admin_id.strip())
    for admin_id in _get_env("ADMIN_IDS", default="").split(",")
    if admin_id.strip().isdigit()
]

ADMIN_ID: int = ADMIN_IDS[0] if ADMIN_IDS else 0


# ─────────────────────────────────────────────────────────────
# Fayl va papka yo'llari
# ─────────────────────────────────────────────────────────────

default_download_dir = "/tmp/downloads" if os.getenv("RENDER") else str(BASE_DIR / "downloads")

DOWNLOAD_DIR: Path = Path(_get_env("DOWNLOAD_DIR", default=default_download_dir))
LOG_FILE: Path = Path(_get_env("LOG_FILE", default=str(BASE_DIR / "bot.log")))
LOG_LEVEL: str = _get_env("LOG_LEVEL", default="INFO").upper()

# Cookie fayllari uchun yo'llar
COOKIES_FILE: Path = Path("/tmp/cookies.txt")
IG_COOKIES_FILE: Path = Path("/tmp/instagram_cookies.txt")  # <-- Mana shu qator yetishmayotgan edi


# ─────────────────────────────────────────────────────────────
# Yuklash cheklovlari
# ─────────────────────────────────────────────────────────────

MAX_FILE_SIZE: int = _get_int("MAX_FILE_SIZE", default=50 * 1024 * 1024)
DOWNLOAD_TIMEOUT: int = _get_int("DOWNLOAD_TIMEOUT", default=300)
CLEANUP_MAX_AGE_MINUTES: int = _get_int("CLEANUP_MAX_AGE_MINUTES", default=30)


# ─────────────────────────────────────────────────────────────
# Xatti-harakat bayroqlari
# ─────────────────────────────────────────────────────────────

NOTIFY_ADMIN_ON_START: bool = _get_bool("NOTIFY_ADMIN_ON_START", default=False)
ENFORCE_SINGLE_DOWNLOAD: bool = _get_bool("ENFORCE_SINGLE_DOWNLOAD", default=True)


# ─────────────────────────────────────────────────────────────
# Tekshiruv
# ─────────────────────────────────────────────────────────────

def validate_config() -> None:
    """Sozlamalar to'g'riligini tekshiradi, papkalarni va cookie fayllarini yaratadi."""
    errors: list[str] = []

    if not BOT_TOKEN:
        errors.append("BOT_TOKEN bo'sh.")
    elif ":" not in BOT_TOKEN or not BOT_TOKEN.split(":", 1)[0].isdigit():
        errors.append("BOT_TOKEN noto'g'ri formatda.")

    if errors:
        raise RuntimeError("Konfiguratsiya xatolari:\n  - " + "\n  - ".join(errors))

    # Papkalarni yaratish
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    # YouTube Cookie faylini yaratish
    yt_cookies_content = os.getenv("YTDL_COOKIES")
    if yt_cookies_content:
        try:
            COOKIES_FILE.write_text(yt_cookies_content.strip(), encoding="utf-8")
            logger.info("YouTube cookies fayli yaratildi: %s", COOKIES_FILE)
        except Exception as e:
            logger.error("YouTube cookies faylini yozishda xatolik: %s", e)
    else:
        logger.warning("YTDL_COOKIES topilmadi.")

    # Instagram Cookie faylini yaratish
    ig_cookies_content = os.getenv("IG_COOKIES")
    if ig_cookies_content:
        try:
            IG_COOKIES_FILE.write_text(ig_cookies_content.strip(), encoding="utf-8")
            logger.info("Instagram cookies fayli yaratildi: %s", IG_COOKIES_FILE)
        except Exception as e:
            logger.error("Instagram cookies faylini yozishda xatolik: %s", e)
    else:
        logger.warning("IG_COOKIES topilmadi.")
