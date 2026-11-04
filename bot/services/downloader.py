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
        # MUHIM: String emas, obyekt bo'lishi kerak
        "impersonate": ImpersonateTarget.from_str("chrome"),
        "remote_components": ["ejs:github"],
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
        
        # YouTube uchun mijozlar va PO Token
        opts["extractor_args"] = {
            "youtube": {
                "player_client": ["ios", "web", "android"],
                "youtubepot-bgutilhttp": {"base_url": ["http://127.0.0.1:4416"]},
            }
        }
        # 1080p va undan yuqori sifat uchun
        opts["format"] = "bestvideo*+bestaudio/best"

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = Path(ydl.prepare_filename(info))
    except yt_dlp.utils.DownloadError as e:
        message = str(e).lower()
        if "sign in to confirm" in message:
            raise DownloadError("YouTube bot deb hisobladi. Cookie faylini yangilang.") from e
        if "private" in message or "not available" in message:
            raise PrivateContentError("Video yopiq yoki mavjud emas.") from e
        raise DownloadError("Videoni yuklab bo'lmadi. Havolani tekshiring.") from e
    except Exception as e:
        logger.exception("Kutilmagan yt-dlp xatoligi: %s", url)
        raise DownloadError("Kutilmagan xatolik yuz berdi.") from e

    if not file_path.exists():
        candidates = list(DOWNLOAD_DIR.glob(f"{unique_prefix}_*"))
        if candidates:
            file_path = candidates[0]

    title = info.get("title") or "Video"
    title = re.sub(r"[\r\n\t]", " ", title).strip()

    return {"file_path": file_path, "title": title}


def download_music(query: str) -> dict:
    """Qo'shiq nomini qidirib, audio (mp3) formatida yuklaydi."""
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    unique_prefix = uuid.uuid4().hex[:8]
    output_template = DOWNLOAD_DIR / f"{unique_prefix}_%(title).100s.%(ext)s"

    opts = _get_base_opts(output_template)
    
    opts["format"] = "bestaudio/best"
    opts["postprocessors"] = [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }]

    if COOKIES_FILE.exists():
        opts["cookiefile"] = str(COOKIES_FILE)

    # Musiqa uchun faqat "android" mijozi eng barqaror hisoblanadi
    opts["extractor_args"] = {
        "youtube": {
            "player_client": ["android"],
            "youtubepot-bgutilhttp": {"base_url": ["http://127.0.0.1:4416"]},
        }
    }

    search_url = f"ytsearch1:{query}"

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(search_url, download=True)
            if "entries" in info:
                info = info["entries"][0]
            file_path = Path(ydl.prepare_filename(info)).with_suffix('.mp3')
    except yt_dlp.utils.DownloadError as e:
        logger.error("Musiqa yuklashda yt-dlp xatoligi: %s", e)
        raise DownloadError(f"'{query}' qo'shig'ini topib bo'lmadi.") from e
    except Exception as e:
        logger.exception("Musiqa yuklashda kutilmagan xatolik: %s", query)
        raise DownloadError("Musiqa yuklashda kutilmagan xatolik yuz berdi.") from e

    if not file_path.exists():
        candidates = list(DOWNLOAD_DIR.glob(f"{unique_prefix}_*.mp3"))
        if candidates:
            file_path = candidates[0]
        else:
            raise DownloadError("Musiqa fayli saqlanmadi.")

    title = info.get("title") or query
    title = re.sub(r"[\r\n\t]", " ", title).strip()

    return {"file_path": file_path, "title": title}
