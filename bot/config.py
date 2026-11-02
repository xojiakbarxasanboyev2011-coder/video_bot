"""
Loyiha sozlamalari.

Barcha konfiguratsiya `.env` faylidan o'qiladi. Bu fayl kodda
token kabi maxfiy ma'lumotlarni saqlamaslik uchun xizmat qiladi.

Foydalanish:
    from bot.config import BOT_TOKEN, DOWNLOAD_DIR, ADMIN_ID
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ─────────────────────────────────────────────────────────────
# .env faylini yuklash
# ─────────────────────────────────────────────────────────────
# `load_dotenv()` loyiha ildizidagi `.env` faylini qidiradi.
# Agar fayl topilmasa, muhit o'zgaruvchilari (environment variables)
# ishlatiladi — bu Docker yoki server uchun qulay.

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# ─────────────────────────────────────────────────────────────
# Yordamchi funksiyalar
# ─────────────────────────────────────────────────────────────

def _get_env(name: str, default: str | None = None, required: bool = False) -> str:
    """
    Muhit o'zgaruvchisini o'qiydi.

    Args:
        name: O'zgaruvchi nomi (masalan, "BOT_TOKEN")
        default: Topilmasa ishlatiladigan qiymat
        required: True bo'lsa va qiymat bo'sh bo'lsa — xatolik ko'taradi

    Raises:
        RuntimeError: `required=True` va qiymat topilmasa
    """
    value = os.getenv(name, default)

    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            raise RuntimeError(
                f"'{name}' muhit o'zgaruvchisi topilmadi. "
                f".env faylini tekshiring (namuna: .env.example)."
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

# @BotFather'dan olingan token — MAJBURIY
BOT_TOKEN: str = _get_env("BOT_TOKEN", required=True)

# Administrator(lar) Telegram ID'si — xatolik haqida xabar olish uchun.
# Vergul bilan bir nechta ID yozish mumkin: "123456789,987654321"
ADMIN_IDS: list[int] = [
    int(admin_id.strip())
    for admin_id in _get_env("ADMIN_IDS", default="").split(",")
    if admin_id.strip().isdigit()
]

# Orqaga moslik uchun birinchi admin (eski kod `ADMIN_ID` ni kutishi mumkin)
ADMIN_ID: int = ADMIN_IDS[0] if ADMIN_IDS else 0


# ─────────────────────────────────────────────────────────────
# Fayl va papka yo'llari
# ─────────────────────────────────────────────────────────────

# Video vaqtinchalik saqlanadigan papka
DOWNLOAD_DIR: Path = Path(_get_env("DOWNLOAD_DIR", default=str(BASE_DIR / "downloads")))

# Log fayli joylashuvi
LOG_FILE: Path = Path(_get_env("LOG_FILE", default=str(BASE_DIR / "bot.log")))

# Log darajasi: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL: str = _get_env("LOG_LEVEL", default="INFO").upper()


# ─────────────────────────────────────────────────────────────
# Yuklash cheklovlari
# ─────────────────────────────────────────────────────────────

# Telegram Bot API orqali maksimal fayl hajmi (baytlarda).
# Standart: 50 MB. Mahalliy Bot API server ishlatsangiz, 2000 MB gacha oshirish mumkin.
MAX_FILE_SIZE: int = _get_int("MAX_FILE_SIZE", default=50 * 1024 * 1024)

# Bitta video yuklash uchun maksimal vaqt (soniyalarda).
# Undan uzoq davom etsa — jarayon to'xtatiladi.
DOWNLOAD_TIMEOUT: int = _get_int("DOWNLOAD_TIMEOUT", default=300)

# Vaqtinchalik fayllar necha daqiqadan keyin tozalanadi (cleanup.py uchun)
CLEANUP_MAX_AGE_MINUTES: int = _get_int("CLEANUP_MAX_AGE_MINUTES", default=30)


# ─────────────────────────────────────────────────────────────
# Xatti-harakat bayroqlari
# ─────────────────────────────────────────────────────────────

# Bot ishga tushganda admin(lar)ga xabar yuborilsinmi?
NOTIFY_ADMIN_ON_START: bool = _get_bool("NOTIFY_ADMIN_ON_START", default=False)

# Foydalanuvchi bir vaqtda faqat bitta yuklashni amalga oshirsinmi?
# (download.py dagi `_active_users` mantig'i bilan bog'liq)
ENFORCE_SINGLE_DOWNLOAD: bool = _get_bool("ENFORCE_SINGLE_DOWNLOAD", default=True)


# ─────────────────────────────────────────────────────────────
# Modul ishga tushganda tekshiruv
# ─────────────────────────────────────────────────────────────

def validate_config() -> None:
    """
    Sozlamalar to'g'ri ekanligini tekshiradi.

    `bot/main.py` da birinchi qadam sifatida chaqiriladi.
    Xatolik bo'lsa — dastur ishga tushmaydi (fail fast).
    """
    errors: list[str] = []

    # Token formati: "123456789:ABCdefGHI..."
    if not BOT_TOKEN:
        errors.append("BOT_TOKEN bo'sh.")
    elif ":" not in BOT_TOKEN or not BOT_TOKEN.split(":", 1)[0].isdigit():
        errors.append(
            "BOT_TOKEN noto'g'ri formatda. "
            "Namuna: 123456789:ABCdefGHI..."
        )

    if MAX_FILE_SIZE <= 0:
        errors.append("MAX_FILE_SIZE musbat son bo'lishi kerak.")

    if DOWNLOAD_TIMEOUT <= 0:
        errors.append("DOWNLOAD_TIMEOUT musbat son bo'lishi kerak.")

    if errors:
        raise RuntimeError(
            "Konfiguratsiya xatolari:\n  - " + "\n  - ".join(errors)
        )

    # Papkalarni yaratish
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────
# Qulay debug: `python -m bot.config` bilan sozlamalarni ko'rish
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Bot konfiguratsiyasi ===")
    print(f"BOT_TOKEN        : {'*' * 10 + BOT_TOKEN[-4:] if BOT_TOKEN else '(bo\'sh)'}")
    print(f"ADMIN_IDS        : {ADMIN_IDS}")
    print(f"DOWNLOAD_DIR     : {DOWNLOAD_DIR}")
    print(f"LOG_FILE         : {LOG_FILE}")
    print(f"LOG_LEVEL        : {LOG_LEVEL}")
    print(f"MAX_FILE_SIZE    : {MAX_FILE_SIZE // (1024 * 1024)} MB")
    print(f"DOWNLOAD_TIMEOUT : {DOWNLOAD_TIMEOUT} s")
    print(f"CLEANUP_MAX_AGE  : {CLEANUP_MAX_AGE_MINUTES} min")
    print(f"ENFORCE_SINGLE   : {ENFORCE_SINGLE_DOWNLOAD}")
