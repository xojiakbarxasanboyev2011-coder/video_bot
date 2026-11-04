"""
Handlers for /start, /help, /about commands and their respective callbacks.

Provides a welcoming interface and clear instructions for the user.
"""

import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_to_menu_keyboard, help_keyboard

logger = logging.getLogger(__name__)
router = Router(name="start_router")


# ─────────────────────────────────────────────────────────────
# Message Texts (English & HTML Formatted)
# ─────────────────────────────────────────────────────────────

WELCOME_TEXT = (
    "👋 <b>Hello, {name}!</b>\n\n"
    "I am your <b>Universal Media Downloader</b>. You can send me a direct link "
    "to a video or simply type the name of a song, and I will fetch it for you.\n\n"
    "🎯 <b>What can I do?</b>\n"
    "🎬 <b>Download Videos:</b> I support YouTube, Instagram, TikTok, Twitter, and 1000+ other sites. (Watermark-free where possible).\n"
    "🎵 <b>Find Music:</b> Just type a song name (e.g., <i>Eminem Lose Yourself</i>), and I will find it on YouTube and send it as an MP3 file.\n\n"
    "🚀 <b>How to use me?</b>\n"
    "1️⃣ Copy a video link and paste it here.\n"
    "<b>OR</b>\n"
    "2️⃣ Simply type the name of the song you want.\n\n"
    "❓ Need more details? Tap /help."
)

HELP_TEXT = (
    "📖 <b>User Guide & Instructions</b>\n\n"
    "📌 <b>1. Downloading Videos</b>\n"
    "Find your desired video (YouTube, Instagram, TikTok, etc.), tap «Share» → «Copy Link», and send it to me. I will download and send the video file directly to you.\n\n"
    "📌 <b>2. Downloading Music (MP3)</b>\n"
    "No links needed. Just type the artist and song name.\n"
    "<i>Example: The Weeknd Blinding Lights</i>\n\n"
    "⚠️ <b>Limitations:</b>\n"
    "• Telegram bots have a maximum file upload limit of <b>50 MB</b>.\n"
    "• Private or restricted account videos cannot be downloaded.\n"
    "• Some sites may occasionally block server requests.\n\n"
    "⚙️ <b>Available Commands:</b>\n"
    "/start — Restart the bot\n"
    "/help — Show this guide\n"
    "/about — Learn more about this bot"
)

ABOUT_TEXT = (
    "ℹ️ <b>About This Bot</b>\n\n"
    "This bot is built using modern, cutting-edge technologies to ensure speed and reliability:\n\n"
    "• <b>Python 3.11</b> — Core programming language\n"
    "• <b>aiogram 3</b> — Asynchronous Telegram Bot framework\n"
    "• <b>yt-dlp</b> — The most powerful video/audio extractor\n"
    "• <b>Docker & PO Token</b> — Used to bypass strict platform protections\n\n"
    "🤖 If you encounter any bugs or have suggestions for new features, please contact the administrator."
)


# ─────────────────────────────────────────────────────────────
# Command Handlers
# ─────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Triggered when a user sends /start."""
    user_name = message.from_user.first_name or "friend"
    logger.info("User %s started the bot", message.from_user.id)

    await message.answer(
        WELCOME_TEXT.format(name=user_name),
        reply_markup=help_keyboard(),
        disable_web_page_preview=True,
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Triggered when a user sends /help."""
    await message.answer(
        HELP_TEXT,
        reply_markup=back_to_menu_keyboard(),
        disable_web_page_preview=True,
    )


@router.message(Command("about"))
async def cmd_about(message: Message) -> None:
    """Triggered when a user sends /about."""
    await message.answer(
        ABOUT_TEXT,
        reply_markup=back_to_menu_keyboard(),
        disable_web_page_preview=True,
    )


# ─────────────────────────────────────────────────────────────
# Callback Query Handlers (For Inline Buttons)
# ─────────────────────────────────────────────────────────────

@router.callback_query(F.data == "show_help")
async def cb_show_help(callback: CallbackQuery) -> None:
    """Triggered when the 'Help' inline button is pressed."""
    await callback.message.answer(
        HELP_TEXT,
        reply_markup=back_to_menu_keyboard(),
        disable_web_page_preview=True,
    )
    await callback.answer()


@router.callback_query(F.data == "show_about")
async def cb_show_about(callback: CallbackQuery) -> None:
    """Triggered when the 'About' inline button is pressed."""
    await callback.message.answer(
        ABOUT_TEXT,
        reply_markup=back_to_menu_keyboard(),
        disable_web_page_preview=True,
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_start")
async def cb_back_to_start(callback: CallbackQuery) -> None:
    """Triggered when the 'Back' inline button is pressed."""
    user_name = callback.from_user.first_name or "friend"
    await callback.message.answer(
        WELCOME_TEXT.format(name=user_name),
        reply_markup=help_keyboard(),
        disable_web_page_preview=True,
    )
    await callback.answer()
