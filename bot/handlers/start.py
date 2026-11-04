"""
/start, /help, /about buyruqlari va ularga tegishli callback'lar.
"""

import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_to_menu_keyboard, help_keyboard

logger = logging.getLogger(__name__)
router = Router(name="start_router")


WELCOME_TEXT = (
    "👋 <b>Salom, {name}!</b>\n\n"
    "Men <b>Universal Media Yuklovchi</b> botman. Menga istalgan video havolasini "
    "yoki shunchaki qo'shiq nomini yuboring — men uni topib, sizga yuboraman.\n\n"
    "🎯 <b>Men nimalarni qila olaman?</b>\n"
    "🎬 <b>Video yuklash:</b> YouTube, Instagram, TikTok, Twitter va boshqa 1000+ saytlardan videolarni yuklayman.\n"
    "🎵 <b>Musiqa topish:</b> Shunchaki qo'shiq nomini yozing (masalan: <i>Eminem Lose Yourself</i>), men uni YouTube'dan topib, MP3 formatida yuboraman.\n\n"
    "🚀 <b>Qanday foydalanish kerak?</b>\n"
    "1. Videoga havolani nusxalab shu yerga tashlang.\n"
    "YOKI\n"
    "2. Qo'shiq nomini oddiy matn qilib yozing.\n\n"
    "❓ Batafsil ma'lumot uchun /help buyrug'ini bosing."
)

HELP_TEXT = (
    "📖 <b>Botdan foydalanish qo'llanmasi</b>\n\n"
    "📌 <b>1. Video yuklash</b>\n"
    "Kerakli videoni toping (YouTube, Instagram, TikTok...), «Ulashish» → «Havolani nusxalash» tugmasini bosing va shu yerga yuboring. Men uni yuklab beraman.\n\n"
    "📌 <b>2. Musiqa (MP3) yuklash</b>\n"
    "Hech qanday havola kerak emas. Shunchaki qo'shiqchi va qo'shiq nomini yozing.\n"
    "<i>Misol: Konsta X - Izlamading</i>\n\n"
    "⚠️ <b>Cheklovlar:</b>\n"
    "• Telegram botlari orqali 50 MB dan katta fayl yuborib bo'lmaydi.\n"
    "• Yopiq (private) akkauntlardagi videolar yuklanmaydi.\n\n"
    "⚙️ <b>Buyruqlar:</b>\n"
    "/start — Botni qayta ishga tushirish\n"
    "/help — Ushbu qo'llanma\n"
    "/about — Bot va uning texnologiyalari haqida"
)

ABOUT_TEXT = (
    "ℹ️ <b>Bot haqida ma'lumot</b>\n\n"
    "Ushbu bot eng zamonaviy texnologiyalar asosida ishlab chiqilgan:\n"
    "• <b>Python 3.11</b> — asosiy dasturlash tili\n"
    "• <b>aiogram 3</b> — Telegram bot framework'i\n"
    "• <b>yt-dlp</b> — dunyodagi eng kuchli video/audio yuklovchi\n"
    "• <b>Docker, Deno, PO Token</b> — YouTube himoyalarini chetlab o'tish uchun\n\n"
    "🤖 Agar botda xatolik sezsangiz yoki taklifingiz bo'lsa, administrator bilan bog'laning."
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Foydalanuvchi /start bosganda ishga tushadi."""
    user_name = message.from_user.first_name or "do'stim"
    logger.info("User %s started the bot", message.from_user.id)

    await message.answer(
        WELCOME_TEXT.format(name=user_name),
        reply_markup=help_keyboard(),
        disable_web_page_preview=True,
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Foydalanuvchi /help bosganda."""
    await message.answer(
        HELP_TEXT,
        reply_markup=back_to_menu_keyboard(),
        disable_web_page_preview=True,
    )


@router.message(Command("about"))
async def cmd_about(message: Message) -> None:
    """Bot haqida ma'lumot."""
    await message.answer(
        ABOUT_TEXT,
        reply_markup=back_to_menu_keyboard(),
        disable_web_page_preview=True,
    )


@router.callback_query(F.data == "show_help")
async def cb_show_help(callback: CallbackQuery) -> None:
    """«Qo'llanma» tugmasi bosilganda."""
    await callback.message.answer(
        HELP_TEXT,
        reply_markup=back_to_menu_keyboard(),
        disable_web_page_preview=True,
    )
    await callback.answer()


@router.callback_query(F.data == "show_about")
async def cb_show_about(callback: CallbackQuery) -> None:
    """«Bot haqida» tugmasi bosilganda."""
    await callback.message.answer(
        ABOUT_TEXT,
        reply_markup=back_to_menu_keyboard(),
        disable_web_page_preview=True,
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_start")
async def cb_back_to_start(callback: CallbackQuery) -> None:
    """Asosiy menyuga qaytish."""
    user_name = callback.from_user.first_name or "do'stim"
    await callback.message.answer(
        WELCOME_TEXT.format(name=user_name),
        reply_markup=help_keyboard(),
        disable_web_page_preview=True,
    )
    await callback.answer()
