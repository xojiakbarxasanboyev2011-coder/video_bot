"""
Handler for downloading Videos and Music.

This module processes user text inputs:
1. If a URL is detected -> Downloads and sends the video.
2. If plain text is detected -> Searches, downloads, and sends the audio as MP3.
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

# Max file size for Telegram Bot API (50 MB)
MAX_FILE_SIZE = 50 * 1024 * 1024

# Track active users to prevent spamming the server
_active_users: set[int] = set()


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text_input(message: Message) -> None:
    """Main handler for all text inputs (Links or Song names)."""
    text = message.text or ""
    url = extract_url(text)
    
    user_id = message.from_user.id

    if user_id in _active_users:
        await message.reply("⏳ Please wait, your previous download is still in progress.")
        return

    _active_users.add(user_id)
    file_path: Path | None = None
    status_msg = None

    try:
        loop = asyncio.get_running_loop()
        
        # ─── 1. PROCESS VIDEO (If a link is provided) ───
        if url:
            status_msg = await message.reply("🔍 Analyzing link...")
            await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_VIDEO)
            await status_msg.edit_text("⬇️ Downloading video, please wait...")

            # Force a 120-second timeout to prevent infinite hanging
            result = await asyncio.wait_for(
                loop.run_in_executor(None, download_video, url),
                timeout=120.0
            )
            
            file_path = result["file_path"]
            title = result["title"]

            if not file_path.exists():
                raise DownloadError("Downloaded file not found.")

            if file_path.stat().st_size > MAX_FILE_SIZE:
                await status_msg.edit_text("❌ Video exceeds the 50 MB Telegram limit. Cannot upload.")
                return

            await status_msg.edit_text("📤 Uploading video...")
            await message.reply_video(
                video=FSInputFile(path=file_path, filename=f"{title[:60]}.mp4"),
                caption=f"✅ <b>{title[:200]}</b>",
                supports_streaming=True,
                reply_markup=after_download_keyboard(),
            )
            await status_msg.delete()

        # ─── 2. PROCESS MUSIC (If plain text is provided) ───
        else:
            if len(text.strip()) < 3:
                await message.reply("❓ Please send me a valid video link or a song name (at least 3 characters).")
                return

            status_msg = await message.reply(f"🎵 Searching for <b>{text}</b>...")
            await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_VOICE)
            await status_msg.edit_text("⬇️ Downloading music, please wait...")

            # Force a 120-second timeout
            result = await asyncio.wait_for(
                loop.run_in_executor(None, download_music, text),
                timeout=120.0
            )
            
            file_path = result["file_path"]
            title = result["title"]

            if not file_path.exists():
                raise DownloadError("Music file not found.")

            if file_path.stat().st_size > MAX_FILE_SIZE:
                await status_msg.edit_text("❌ Audio file exceeds the 50 MB Telegram limit.")
                return

            await status_msg.edit_text("📤 Uploading music...")
            await message.reply_audio(
                audio=FSInputFile(path=file_path, filename=f"{title[:60]}.mp3"),
                title=title[:100],
                performer="YouTube",
                reply_markup=after_download_keyboard(),
            )
            await status_msg.delete()

    except asyncio.TimeoutError:
        logger.warning("Download timed out for: %s", text)
        if status_msg:
            await status_msg.edit_text(
                "❌ <b>Download timed out (2 minutes).</b>\n"
                "The platform server is not responding. Please try again later."
            )

    except DownloadError as e:
        logger.warning("DownloadError: %s", e)
        if status_msg:
            await status_msg.edit_text(f"❌ {e}")
        else:
            await message.reply(f"❌ {e}")

    except Exception:
        logger.exception("Unexpected error during download")
        if status_msg:
            await status_msg.edit_text("❌ An unexpected error occurred. Please try again later.")
        else:
            await message.reply("❌ An unexpected error occurred.")

    finally:
        # Clean up
        _active_users.discard(user_id)
        if file_path is not None and file_path.exists():
            try:
                os.remove(file_path)
            except OSError as e:
                logger.warning("Failed to delete temp file %s: %s", file_path, e)


@router.callback_query(F.data == "new_download")
async def cb_new_download(callback: CallbackQuery) -> None:
    """Triggered when the user clicks the 'Download another' button."""
    await callback.message.answer("📎 Send me a new video link or song name.")
    await callback.answer()
