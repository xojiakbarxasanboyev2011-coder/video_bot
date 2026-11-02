"""
Loyiha sozlamalari.

Barcha konfiguratsiya `.env` faylidan yoki Render'dagi muhit
o'zgaruvchilaridan (Environment Variables) o'qiladi.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ─────────────────────────────────────────────────────────────
# .env faylini yuklash
# ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# ─────────────────────────────────────────────────────────────
# Yordamchi funksiyalar
# ─────────────────────────────────────────────────────────────

def _get_env(name: str, default: str | None = None, required: bool = False) -> str:
    """Muhit o'zgaruvchisini xavfsiz o'qiydi."""
    value = os.getenv(name, default)

    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            raise RuntimeError(
                f"'{name}' muhit o'zgaruvchisi topilmadi. "
                f".env faylini yoki platforma sozlamalarini tekshiring."
            )
        return default or ""

    return value.strip()


def _get_int(name: str, default: int = 0) -> int:
    """Butun son o'zgaruvchisini xavfsiz o'qiydi."""
    raw = _get_env(name, default=str(default))
    try:
        return int(raw)
    except ValueError:
        return default


def _get_bool(name: str, default: bool = False) -> bool:
    """Mantiqiy (True/False) o'zgaruvchisini o'qiydi."""
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
# Render'da vaqtinchalik papkalar faqat /tmp ichida ishlaydi.
# Shuning uchun agar muhit o'zgaruvchisi berilmagan bo'lsa, /tmp ishlatiladi.
default_download_dir = "/tmp/downloads" if os.getenv("RENDER") else str(BASE_DIR / "downloads")

DOWNLOAD_DIR: Path = Path(_get_env("DOWNLOAD_DIR", default=default_download_dir))
LOG_FILE: Path = Path(_get_env("LOG_FILE", default=str(BASE_DIR / "bot.log")))
LOG_LEVEL: str = _get_env("LOG_LEVEL", default="INFO").upper()


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
    """Sozlamalar to'g'riligini tekshiradi va kerakli papkalarni yaratadi."""
    errors: list[str] = []

    if not BOT_TOKEN:
        errors.append("BOT_TOKEN bo'sh.")
    elif ":" not in BOT_TOKEN or not BOT_TOKEN.split(":", 1)[0].isdigit():
        errors.append("BOT_TOKEN noto'g'ri formatda (123456789:ABCdef... ko'rinishida bo'lishi kerak).")

    if MAX_FILE_SIZE <= 0:
        errors.append("MAX_FILE_SIZE musbat son bo'lishi kerak.")

    if DOWNLOAD_TIMEOUT <= 0:
        errors.append("DOWNLOAD_TIMEOUT musbat son bo'lishi kerak.")

    if errors:
        raise RuntimeError("Konfiguratsiya xatolari:\n  - " + "\n  - ".join(errors))

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────
# Qulay debug
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Python 3.11 dagi xatolik tuzatildi (f-string ichida backslash yo'q)
    token_display = ("*" * 10 + BOT_TOKEN[-4:]) if BOT_TOKEN else "(kiritilmagan)"
    
    print("=== Bot konfiguratsiyasi ===")
    print(f"BOT_TOKEN        : {token_display}")
    print(f"ADMIN_IDS        : {ADMIN_IDS}")
    print(f"DOWNLOAD_DIR     : {DOWNLOAD_DIR}")
    print(f"LOG_FILE         : {LOG_FILE}")
    print(f"LOG_LEVEL        : {LOG_LEVEL}")
    print(f"MAX_FILE_SIZE    : {MAX_FILE_SIZE // (1024 * 1024)} MB")
    print(f"DOWNLOAD_TIMEOUT : {DOWNLOAD_TIMEOUT} s")
    print(f"CLEANUP_MAX_AGE  : {CLEANUP_MAX_AGE_MINUTES} min")
    print(f"ENFORCE_SINGLE   : {ENFORCE_SINGLE_DOWNLOAD}")
