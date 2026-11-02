"""
yt-dlp bilan ishlash.

Platformaga qarab format tanlaydi (TikTok uchun watermark bo'lmagan
oqim), videoni yuklab oladi va natija haqida dict qaytaradi.

Bu modul SINXRON ishlaydi — handler'lar uni `run_in_executor` orqali
chaqirishi shart, aks holda bot qotib qoladi.
"""

import logging
import re
import uuid
from pathlib import Path

import yt_dlp

from bot.config import DOWNLOAD_DIR

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Xatolik turlari
# ─────────────────────────────────────────────────────────────

class DownloadError(Exception):
    """Barcha yuklash xatoliklari uchun asosiy sinf. Xabar foydalanuvchiga ko'rsatiladi."""


class VideoTooLargeError(DownloadError):
    """Video Telegram chegarasidan katta."""


class PrivateContentError(DownloadError):
    """Video yopiq, o'chirilgan yoki mavjud emas."""


# ─────────────────────────────────────────────────────────────
# Format strategiyasi
# ─────────────────────────────────────────────────────────────

def _build_ydl_opts(url: str, output_path: Path) -> dict:
    """
    Platformaga qarab yt-dlp sozlamalarini qaytaradi.

    - TikTok: `format="b"` (best single stream) — watermark bo'lmagan versiya
    - Instagram: `format="best"` — watermarkli bo'lishi mumkin, lekin
      mavjud eng yaxshi oqim
    - YouTube va boshqalar: mp4 afzal ko'riladi
    """
    opts: dict = {
        "outtmpl": str(output_path),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        # Fayl nomida noto'g'ri belgilarni cheklash
        "restrictfilenames": True,
        "logger": logger,
    }

    url_lower = url.lower()

    if "tiktok.com" in url_lower:
        # Watermark bo'lmagan yagona oqim
        opts["format"] = "b"
    elif "instagram.com" in url_lower:
        opts["format"] = "best"
    else:
        # YouTube va boshqalar uchun mp4 afzal
        opts["format"] = "best[ext=mp4]/best"

    return opts


# ─────────────────────────────────────────────────────────────
# Asosiy funksiya
# ─────────────────────────────────────────────────────────────

def download_video(url: str) -> dict:
    """
    Videoni yuklab oladi.

    Qaytaradi:
        {"file_path": Path, "title": str, "ext": str}

    Xatolikda `DownloadError` (yoki uning avlodi) ko'taradi.
    """
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Har bir yuklash uchun unikal prefiks — parallel yuklashlarda to'qnashuv bo'lmasin
    unique_prefix = uuid.uuid4().hex[:8]
    output_template = DOWNLOAD_DIR / f"{unique_prefix}_%(title).100s.%(ext)s"

    ydl_opts = _build_ydl_opts(url, output_template)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = Path(ydl.prepare_filename(info))

    except yt_dlp.utils.DownloadError as e:
        message = str(e).lower()
        # Xato matnini tahlil qilib, foydalanuvchiga tushunarli xabar beramiz
        if "private" in message or "login" in message or "not available" in message:
            raise PrivateContentError(
                "Video yopiq (private), o'chirilgan yoki mavjud emas."
            ) from e
        if "unsupported url" in message:
            raise DownloadError("Bu sayt qo'llab-quvvatlanmaydi.") from e
        if "403" in message or "forbidden" in message:
            raise DownloadError(
                "Sayt so'rovni blokladi. Keyinroq qayta urinib ko'ring."
            ) from e
        raise DownloadError("Videoni yuklab bo'lmadi.") from e

    except Exception as e:
        logger.exception("Unexpected yt-dlp error for %s", url)
        raise DownloadError("Kutilmagan xatolik yuz berdi.") from e

    # Ba'zi hollarda prepare_filename kengaytmani noto'g'ri qaytaradi
    # (masalan, .webm yuklangan bo'lsa). Diskda mavjud faylni topamiz.
    if not file_path.exists():
        candidates = list(DOWNLOAD_DIR.glob(f"{unique_prefix}_*"))
        if candidates:
            file_path = candidates[0]

    title = info.get("title") or "Video"
    # Fayl nomida xavfli belgilarni tozalash (Telegram uchun)
    title = re.sub(r"[\r\n\t]", " ", title).strip()

    return {
        "file_path": file_path,
        "title": title,
        "ext": info.get("ext", "mp4"),
    }
