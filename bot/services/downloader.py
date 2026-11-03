"""
yt-dlp bilan ishlash.
"""

import logging
import re
import uuid
from pathlib import Path

import yt_dlp

from bot.config import DOWNLOAD_DIR, COOKIES_FILE, IG_COOKIES_FILE

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """Barcha yuklash xatoliklari uchun asosiy sinf."""


class VideoTooLargeError(DownloadError):
    """Video Telegram chegarasidan katta."""


class PrivateContentError(DownloadError):
    """Video yopiq, o'chirilgan yoki mavjud emas."""


def _build_ydl_opts(url: str, output_path: Path) -> dict:
    """Platformaga qarab yt-dlp sozlamalarini qaytaradi."""
    opts: dict = {
        "outtmpl": str(output_path),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "restrictfilenames": True,
        "logger": logger,
        # Xatolik shu yerda edi: ro'yxat emas, lug'at bo'lishi kerak
        "js_runtimes": {"deno": {}}, 
        "impersonate": "chrome",
    }

    url_lower = url.lower()

    if "instagram.com" in url_lower:
        if IG_COOKIES_FILE.exists():
            opts["cookiefile"] = str(IG_COOKIES_FILE)
        opts["format"] = "best"
    elif "tiktok.com" in url_lower:
        opts["format"] = "b"
    else:  # YouTube va boshqalar
        if COOKIES_FILE.exists():
            opts["cookiefile"] = str(COOKIES_FILE)
        opts["format"] = "best[ext=mp4]/best"

    return opts


def download_video(url: str) -> dict:
    """Videoni yuklab oladi."""
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    unique_prefix = uuid.uuid4().hex[:8]
    output_template = DOWNLOAD_DIR / f"{unique_prefix}_%(title).100s.%(ext)s"

    ydl_opts = _build_ydl_opts(url, output_template)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = Path(ydl.prepare_filename(info))

    except yt_dlp.utils.DownloadError as e:
        message = str(e).lower()
        if "sign in to confirm" in message:
            raise DownloadError("YouTube bot deb hisobladi. Cookie faylini yangilang yoki birozdan so'ng qayta urinib ko'ring.") from e
        if "login required" in message or "empty media" in message:
            raise DownloadError("Instagram videoni yuklash uchun tizimga kirish talab qilinadi.") from e
        if "private" in message or "not available" in message:
            raise PrivateContentError("Video yopiq yoki mavjud emas.") from e
        if "unsupported url" in message:
            raise DownloadError("Bu sayt qo'llab-quvvatlanmaydi.") from e
        raise DownloadError("Videoni yuklab bo'lmadi.") from e

    except Exception as e:
        logger.exception("Unexpected yt-dlp error for %s", url)
        raise DownloadError("Kutilmagan xatolik yuz berdi.") from e

    if not file_path.exists():
        candidates = list(DOWNLOAD_DIR.glob(f"{unique_prefix}_*"))
        if candidates:
            file_path = candidates[0]

    title = info.get("title") or "Video"
    title = re.sub(r"[\r\n\t]", " ", title).strip()

    return {
        "file_path": file_path,
        "title": title,
        "ext": info.get("ext", "mp4"),
    }
