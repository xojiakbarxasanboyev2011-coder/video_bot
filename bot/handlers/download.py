"""
Video yuklash handler'i.

Foydalanuvchi yuborgan havolani qabul qiladi, yt-dlp orqali videoni
yuklab oladi va uni Telegram orqali qaytaradi. Xatoliklar, 50 MB
limiti va bir foydalanuvchi uchun blokirovka hisobga olingan.
"""

import asyncio
import logging
import os
from pathlib import Path

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.types import CallbackQuery, FSInputFile, Message

from bot.keyboards import after_download_keyboard
from bot.services.downloader import DownloadError, download_video
from bot.utils.validators import extract_url, is_supported_url

logger = logging.getLogger(__name__)
router = Router(name="download_router")

# Telegram Bot API orqali yuboriladigan maksimal fayl hajmi (50 MB)
MAX_FILE_SIZE = 50 * 1024 * 1024

# Bir vaqtning o'zida bitta foydalanuvchi uchun yuklashni bloklash uchun
_active_users: set[int] = set()


# ─────────────────────────────────────────────────────────────
# Asosiy handler
# ─────────────────────────────────────────────────────────────

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

    file_path: Path | None = None

    try:
        await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)
        await status_msg.edit_text("⬇️ Video yuklanmoqda, iltimos kuting...")

        # yt-dlp sinxron — alohida oqimda ishga tushiriladi
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, download_video, url)

        file_path = Path(result["file_path"])
        title: str = result.get("title", "Video")

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
            reply_markup=after_download_keyboard(),
        )

        # Status xabarini o'chirish (endi kerak emas)
        await status_msg.delete()

    except DownloadError as e:
        logger.warning("Download failed for %s: %s", url, e)
        await status_msg.edit_text(f"❌ Yuklab bo'lmadi: {e}")

    except Exception:
        logger.exception("Unexpected error for %s", url)
        await status_msg.edit_text(
            "❌ Kutilmagan xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring."
        )

    finally:
        _active_users.discard(user_id)
        # Vaqtinchalik faylni tozalash
        if file_path is not None:
            try:
                if file_path.exists():
                    os.remove(file_path)
            except OSError as e:
                logger.warning("Failed to remove temp file %s: %s", file_path, e)


# ─────────────────────────────────────────────────────────────
# Callback handler'lar
# ─────────────────────────────────────────────────────────────

@router.callback_query(F.data == "new_download")
async def cb_new_download(callback: CallbackQuery) -> None:
    """«Yana video yuklash» tugmasi bosilganda."""
    await callback.message.answer(
        "📎 Menga yangi video havolasini yuboring."
    )
    await callback.answer()


@router.callback_query(F.data == "show_help_from_download")
async def cb_show_help_from_download(callback: CallbackQuery) -> None:
    """
    Video yuborilgandan keyingi «Yordam» tugmasi bosilganda.
    `start.py` dagi `show_help` callback'iga yo'naltiradi — buning uchun
    Telegram callback emas, oddiy xabar yuboramiz.
    """
    from bot.handlers.start import HELP_TEXT, back_to_menu_keyboard

    await callback.message.answer(
        HELP_TEXT,
        reply_markup=back_to_menu_keyboard(),
        disable_web_page_preview=True,
    )
    await callback.answer()
