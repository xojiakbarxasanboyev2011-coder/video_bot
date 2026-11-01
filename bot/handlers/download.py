"""
Video yuklash handler'i.

Foydalanuvchi yuborgan havolani qabul qiladi, yt-dlp orqali videoni
yuklab oladi va uni Telegram orqali qaytaradi.
"""

import asyncio
import logging
import os
import re
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.enums import ChatAction

from bot.services.downloader import download_video, DownloadError
from bot.utils.validators import extract_url, is_supported_url

logger = logging.getLogger(__name__)
router = Router(name="download_router")

# Telegram Bot API orqali yuboriladigan maksimal fayl hajmi (50 MB)
MAX_FILE_SIZE = 50 * 1024 * 1024

# Bir vaqtning o'zida bitta foydalanuvchi uchun yuklashni bloklash uchun
# (foydalanuvchi ketma-ket bir nechta havola yuborsa, resurs tejaladi)
_active_users: set[int] = set()


@router.message(F.text & ~F.text.startswith("/"))
async def handle_video_link(message: Message) -> None:
    """
    Matnli xabarni qabul qiladi. Agar matn ichida qo'llab-quvvatlanadigan
    havola bo'lsa — videoni yuklab beradi.
    """
    url = extract_url(message.text or "")

    if not url:
        await message.reply(
            "❓ Menga video havolasini yuboring.\n"
            "Masalan: <code>https://www.instagram.com/reel/...</code>"
        )
        return

    if not is_supported_url(url):
        await message.reply(
            "⚠️ Bu havola qo'llab-quvvatlanmaydi.\n"
            "YouTube, Instagram, TikTok yoki boshqa mashhur saytlardan "
            "havola yuboring."
        )
        return

    user_id = message.from_user.id

    # Bir foydalanuvchi bir vaqtda faqat bitta yuklashni amalga oshiradi
    if user_id in _active_users:
        await message.reply("⏳ Avvalgi videongiz hali yuklanmoqda, iltimos kuting.")
        return

    _active_users.add(user_id)
    status_msg = await message.reply("🔍 Havola tekshirilmoqda...")

    try:
        # Telegram'ga "video yuborilmoqda" holatini ko'rsatamiz
        await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)

        # yt-dlp sinxron — alohida oqimda ishga tushiriladi
        await status_msg.edit_text("⬇️ Video yuklanmoqda, iltimos kuting...")

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, download_video, url)

        file_path: Path = result["file_path"]
        title: str = result.get("title", "Video")

        # Fayl mavjudligini tekshirish
        if not file_path.exists():
            raise DownloadError("Yuklangan fayl topilmadi.")

        # Telegram 50 MB limitini tekshirish
        file_size = file_path.stat().st_size
        if file_size > MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            await status_msg.edit_text(
                f"❌ Video hajmi {size_mb:.1f} MB — Telegram chegarasidan "
                f"(50 MB) katta.\n"
                f"Bu videoni yuborib bo'lmaydi."
            )
            return

        # Videoni foydalanuvchiga yuborish
        await status_msg.edit_text("📤 Video yuborilmoqda...")
        await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)

        video_file = FSInputFile(path=file_path, filename=f"{title[:60]}.mp4")
        await message.reply_video(
            video=video_file,
            caption=f"✅ <b>{title[:200]}</b>",
            supports_streaming=True,
        )

        # Muvaffaqiyatli yuborilgach, status xabarini o'chirish
        await status_msg.delete()

    except DownloadError as e:
        logger.warning("Download failed for %s: %s", url, e)
        await status_msg.edit_text(f"❌ Yuklab bo'lmadi: {e}")

    except Exception as e:
        logger.exception("Unexpected error for %s", url)
        await status_msg.edit_text(
            "❌ Kutilmagan xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring."
        )

    finally:
        _active_users.discard(user_id)
        # Vaqtinchalik faylni tozalash
        try:
            if "file_path" in locals() and file_path.exists():
                os.remove(file_path)
        except OSError as e:
            logger.warning("Failed to remove temp file %s: %s", file_path, e)
