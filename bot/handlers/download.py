"""
Video va Musiqa yuklash handler'i.
"""

import asyncio
import logging
import os
from pathlib import Path

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.types import CallbackQuery, FSInputFile, Message

from bot.keyboards import after_download_keyboard
from bot.services.downloader import DownloadError, download_video, download_music
from bot.utils.validators import extract_url

logger = logging.getLogger(__name__)
router = Router(name="download_router")

MAX_FILE_SIZE = 50 * 1024 * 1024
_active_users: set[int] = set()


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text_input(message: Message) -> None:
    """Havola bo'lsa video, oddiy matn bo'lsa musiqa yuklaydi."""
    text = message.text or ""
    url = extract_url(text)
    
    user_id = message.from_user.id

    if user_id in _active_users:
        await message.reply("⏳ Avvalgi yuklanishingiz tugamadi, iltimos kuting.")
        return

    _active_users.add(user_id)
    file_path: Path | None = None
    status_msg = None

    try:
        loop = asyncio.get_running_loop()
        
        # ─── 1. Agar havola bo'lsa (VIDEO) ───
        if url:
            status_msg = await message.reply("🔍 Havola tekshirilmoqda...")
            await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)
            await status_msg.edit_text("⬇️ Video yuklanmoqda, iltimos kuting...")

            # 120 soniya vaqt chegarasi
            result = await asyncio.wait_for(
                loop.run_in_executor(None, download_video, url),
                timeout=120.0
            )
            
            file_path = result["file_path"]
            title = result["title"]

            if not file_path.exists():
                raise DownloadError("Yuklangan fayl topilmadi.")

            if file_path.stat().st_size > MAX_FILE_SIZE:
                await status_msg.edit_text("❌ Video hajmi 50 MB dan katta. Telegram orqali yuborib bo'lmaydi.")
                return

            await status_msg.edit_text("📤 Video yuborilmoqda...")
            await message.reply_video(
                video=FSInputFile(path=file_path, filename=f"{title[:60]}.mp4"),
                caption=f"✅ <b>{title[:200]}</b>",
                supports_streaming=True,
                reply_markup=after_download_keyboard(),
            )
            await status_msg.delete()

        # ─── 2. Agar havola bo'lmasa (MUSIQA) ───
        else:
            if len(text.strip()) < 3:
                await message.reply("❓ Menga video havolasini yoki qo'shiq nomini yuboring.")
                return

            status_msg = await message.reply(f"🎵 <b>{text}</b> qidirilmoqda...")
            await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_VOICE)
            await status_msg.edit_text("⬇️ Musiqa yuklanmoqda, iltimos kuting...")

            # 120 soniya vaqt chegarasi
            result = await asyncio.wait_for(
                loop.run_in_executor(None, download_music, text),
                timeout=120.0
            )
            
            file_path = result["file_path"]
            title = result["title"]

            if not file_path.exists():
                raise DownloadError("Musiqa fayli topilmadi.")

            if file_path.stat().st_size > MAX_FILE_SIZE:
                await status_msg.edit_text("❌ Musiqa hajmi 50 MB dan katta.")
                return

            await status_msg.edit_text("📤 Musiqa yuborilmoqda...")
            await message.reply_audio(
                audio=FSInputFile(path=file_path, filename=f"{title[:60]}.mp3"),
                title=title[:100],
                performer="YouTube",
                reply_markup=after_download_keyboard(),
            )
            await status_msg.delete()

    except asyncio.TimeoutError:
        logger.warning("Yuklash vaqti tugadi: %s", text)
        if status_msg:
            await status_msg.edit_text("❌ Yuklash vaqti tugadi (2 daqiqa). YouTube serveri javob bermayapti. Keyinroq qayta urinib ko'ring.")

    except DownloadError as e:
        logger.warning("Xatolik: %s", e)
        if status_msg:
            await status_msg.edit_text(f"❌ {e}")
        else:
            await message.reply(f"❌ {e}")

    except Exception:
        logger.exception("Kutilmagan xatolik")
        if status_msg:
            await status_msg.edit_text("❌ Kutilmagan xatolik yuz berdi. Keyinroq qayta urinib ko'ring.")
        else:
            await message.reply("❌ Kutilmagan xatolik yuz berdi.")

    finally:
        _active_users.discard(user_id)
        if file_path is not None and file_path.exists():
            try:
                os.remove(file_path)
            except OSError:
                pass


@router.callback_query(F.data == "new_download")
async def cb_new_download(callback: CallbackQuery) -> None:
    await callback.message.answer("📎 Menga yangi video havolasini yoki qo'shiq nomini yuboring.")
    await callback.answer()
