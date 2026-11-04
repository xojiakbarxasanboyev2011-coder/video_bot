"""
yt-dlp bilan ishlash (Video va Musiqa).
"""

import logging
import re
import uuid
from pathlib import Path

import yt_dlp
from yt_dlp.networking.impersonate import ImpersonateTarget

from bot.config import DOWNLOAD_DIR, COOKIES_FILE, IG_COOKIES_FILE

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """Barcha yuklash xatoliklari uchun asosiy sinf."""


class VideoTooLargeError(DownloadError):
    """Video Telegram chegarasidan katta."""


class PrivateContentError(DownloadError):
    """Video yopiq, o'chirilgan yoki mavjud emas."""


def _get_base_opts(output_path: Path) -> dict:
    """Barcha yuklashlar uchun umumiy sozlamalar."""
    return {
        "outtmpl": str(output_path),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "restrictfilenames": True,
        "logger": logger,
        "js_runtimes": {"deno": {}},
        "impersonate": ImpersonateTarget.from_str("chrome"),
        "remote_components": ["ejs"],
    }


def download_video(url: str) -> dict:
    """Videoni yuklab oladi (havola orqali)."""
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    unique_prefix = uuid.uuid4().hex[:8]
    output_template = DOWNLOAD_DIR / f"{unique_prefix}_%(title).100s.%(ext)s"

    opts = _get_base_opts(output_template)
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
        opts["extractor_args"] = {
            "youtube": {
                "player_client": ["mweb", "android"],
                "youtubepot-bgutilhttp": {"base_url": ["http://127.0.0.1:4416"]},
            }
        }
        opts["format"] = "bestvideo*+bestaudio/best"

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = Path(ydl.prepare_filename(info))
    except Exception as e:
        logger.error("Video yuklashda xatolik: %s", e)
        raise DownloadError("Videoni yuklab bo'lmadi. Havolani tekshiring.")

    if not file_path.exists():
        candidates = list(DOWNLOAD_DIR.glob(f"{unique_prefix}_*"))
        if candidates:
            file_path = candidates[0]

    title = info.get("title") or "Video"
    title = re.sub(r"[\r\n\t]", " ", title).strip()

    return {"file_path": file_path, "title": title}


def download_music(query: str) -> dict:
    """
    Qo'shiq nomini qidirib, audio (mp3) formatida yuklaydi.
    """
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    unique_prefix = uuid.uuid4().hex[:8]
    # Musiqa uchun fayl nomi
    output_template = DOWNLOAD_DIR / f"{unique_prefix}_%(title).100s.%(ext)s"

    opts = _get_base_opts(output_template)
    
    # Audio ajratib olish sozlamalari
    opts["format"] = "bestaudio/best"
    opts["postprocessors"] = [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }]

    if COOKIES_FILE.exists():
        opts["cookiefile"] = str(COOKIES_FILE)

    opts["extractor_args"] = {
        "youtube": {
            "player_client": ["mweb", "android"],
            "youtubepot-bgutilhttp": {"base_url": ["http://127.0.0.1:4416"]},
        }
    }

    # ytsearch1: - YouTube'dan qidirib, eng birinchi natijani oladi
    search_url = f"ytsearch1:{query}"

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(search_url, download=True)
            
            # ytsearch natijasi list (entries) ko'rinishida keladi
            if "entries" in info:
                info = info["entries"][0]
            
            # Post-processordan keyin kengaytma .mp3 bo'ladi
            file_path = Path(ydl.prepare_filename(info)).with_suffix('.mp3')

    except Exception as e:
        logger.error("Musiqa yuklashda xatolik: %s", e)
        raise DownloadError(f"'{query}' qo'shig'ini topib bo'lmadi yoki yuklab bo'lmadi.")

    if not file_path.exists():
        # Agar .with_suffix ishlamasa, papkadan qidiramiz
        candidates = list(DOWNLOAD_DIR.glob(f"{unique_prefix}_*.mp3"))
        if candidates:
            file_path = candidates[0]
        else:
            raise DownloadError("Musiqa fayli saqlanmadi.")

    title = info.get("title") or query
    title = re.sub(r"[\r\n\t]", " ", title).strip()

    return {"file_path": file_path, "title": title}
