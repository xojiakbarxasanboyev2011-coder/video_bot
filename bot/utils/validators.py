"""
URL validatsiyasi va platformani aniqlash.

`yt-dlp` 1800+ saytni qo'llab-quvvatlaydi, lekin bizning botda eng
ko'p ishlatiladigan platformalarni alohida ajratamiz — bu logging va
kelajakdagi statistika uchun foydali.
"""

import re
from urllib.parse import urlparse

# Matndagi birinchi http(s) havolani topadi.
# `[^\s]+` — bo'sh joygacha bo'lgan barcha belgilar.
_URL_REGEX = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)


# Bot qo'llab-quvvatlaydigan platformalar — domen bo'yicha
# (kalit: platforma nomi, qiymat: domenlar ro'yxati)
SUPPORTED_PLATFORMS: dict[str, tuple[str, ...]] = {
    "youtube": ("youtube.com", "youtu.be", "m.youtube.com", "music.youtube.com"),
    "instagram": ("instagram.com", "www.instagram.com", "instagr.am"),
    "tiktok": ("tiktok.com", "vm.tiktok.com", "vt.tiktok.com"),
    "twitter": ("twitter.com", "x.com", "t.co"),
    "facebook": ("facebook.com", "fb.watch", "fb.com"),
    "vimeo": ("vimeo.com",),
    "reddit": ("reddit.com", "redd.it"),
    "pinterest": ("pinterest.com", "pin.it"),
    "twitch": ("twitch.tv",),
    "soundcloud": ("soundcloud.com",),
}

# Barcha domenlarni tekis ro'yxatga yig'amiz — tekshirish uchun qulay
_ALL_DOMAINS: tuple[str, ...] = tuple(
    domain for domains in SUPPORTED_PLATFORMS.values() for domain in domains
)


def extract_url(text: str) -> str | None:
    """
    Matndan birinchi http(s) havolani ajratib oladi.

    >>> extract_url("Mana video: https://youtu.be/abc123 rahmat")
    'https://youtu.be/abc123'
    >>> extract_url("havola yo'q") is None
    True
    """
    if not text:
        return None

    match = _URL_REGEX.search(text)
    if not match:
        return None

    # Oxiridagi tinish belgilarini tozalash (masalan, "...com/reel/abc.")
    url = match.group(0).rstrip(".,;:!?)]}\"'")

    # Havola juda qisqa bo'lsa (masalan "http://a") — rad etamiz
    if len(url) < 12:
        return None

    return url


def detect_platform(url: str) -> str | None:
    """
    URL qaysi platformaga tegishli ekanligini aniqlaydi.

    >>> detect_platform("https://www.instagram.com/reel/xyz/")
    'instagram'
    >>> detect_platform("https://example.com/video") is None
    True
    """
    try:
        host = urlparse(url).hostname or ""
    except ValueError:
        return None

    host = host.lower().removeprefix("www.")

    for platform, domains in SUPPORTED_PLATFORMS.items():
        for domain in domains:
            # `youtube.com` ni `m.youtube.com` ham qamrab olishi uchun
            normalized = domain.lower().removeprefix("www.")
            if host == normalized or host.endswith("." + normalized):
                return platform

    return None


def is_supported_url(url: str) -> bool:
    """
    URL bot tomonidan qo'llab-quvvatlanadimi?

    Aniqlik uchun `yt-dlp` ning to'liq ro'yxatiga tayanmaymiz —
    `SUPPORTED_PLATFORMS` dagi mashhur saytlar bilan cheklanamiz.
    Bu noto'g'ri yoki zararli havolalarni ertaroq filtrlash imkonini beradi.
    """
    return detect_platform(url) is not None
