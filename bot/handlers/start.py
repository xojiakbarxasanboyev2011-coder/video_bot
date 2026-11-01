"""
/start, /help va /about buyruqlari uchun handler'lar.

Foydalanuvchini kutib oladi, bot imkoniyatlarini tushuntiradi va
qo'shimcha ma'lumot beradi.
"""

import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

logger = logging.getLogger(__name__)
router = Router(name="start_router")


# Bot haqida qisqacha ma'lumot — bir joyda saqlash osonroq
WELCOME_TEXT = (
    "👋 <b>Salom, {name}!</b>\n\n"
    "Men video yuklovchi botman. Menga istalgan ijtimoiy tarmoqdan "
    "havola yuboring — men videoni <b>watermarklarsiz</b> yuklab beraman.\n\n"
    "🎯 <b>Qo'llab-quvvatlanadigan saytlar:</b>\n"
    "• YouTube (Shorts, oddiy videolar)\n"
    "• Instagram (Reels, IGTV, postlar)\n"
    "• TikTok\n"
    "• Twitter / X\n"
    "• Facebook\n"
    "• Va yana 1800+ sayt\n\n"
    "📎 <b>Qanday foydalanish kerak?</b>\n"
    "Shunchaki video havolasini nusxalab, shu yerga yuboring.\n\n"
    "❓ Yordam uchun /help buyrug'ini bosing."
)

HELP_TEXT = (
    "📖 <b>Botdan foydalanish qo'llanmasi</b>\n\n"
    "<b>1-qadam.</b> Kerakli videoni toping (YouTube, Instagram, TikTok...)\n"
    "<b>2-qadam.</b> «Ulashish» → «Havolani nusxalash» tugmasini bosing\n"
    "<b>3-qadam.</b> Havolani shu botga yuboring\n"
    "<b>4-qadam.</b> Bir necha soniyadan so'ng videoni olasiz ✅\n\n"
    "<b>⚠️ Cheklovlar:</b>\n"
    "• Video hajmi <b>50 MB</b> dan oshmasligi kerak\n"
    "• Yopiq (private) postlar yuklanmaydi\n"
    "• Ba'zi saytlar vaqtincha ishlamasligi mumkin\n\n"
    "<b>Buyruqlar:</b>\n"
    "/start — Botni qayta ishga tushirish\n"
    "/help — Ushbu qo'llanma\n"
    "/about — Bot haqida ma'lumot"
)

ABOUT_TEXT = (
    "ℹ️ <b>Bot haqida</b>\n\n"
    "Bu bot <code>yt-dlp</code> va <code>aiogram 3</code> asosida qurilgan "
    "ochiq kodli loyihadir.\n\n"
    "🔧 <b>Texnologiyalar:</b>\n"
    "• Python 3.10+\n"
    "• aiogram 3.x\n"
    "• yt-dlp\n\n"
    "📬 <b>Taklif va shikoyatlar:</b>\n"
    "Muammo yuz bersa, administrator bilan bog'laning."
)


def _help_keyboard() -> InlineKeyboardMarkup:
    """Foydalanuvchiga foydali havolalar va tugmalar."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📖 Qo'llanma", callback_data="show_help")
    builder.button(text="ℹ️ Bot haqida", callback_data="show_about")
    builder.adjust(2)  # ikkita tugma bir qatorda
    return builder.as_markup()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Foydalanuvchi /start bosganda ishga tushadi."""
    user_name = message.from_user.first_name or "do'stim"
    logger.info("User %s started the bot", message.from_user.id)

    await message.answer(
        WELCOME_TEXT.format(name=user_name),
        reply_markup=_help_keyboard(),
        disable_web_page_preview=True,
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Foydalanuvchi /help bosganda batafsil qo'llanmani ko'rsatadi."""
    await message.answer(HELP_TEXT, disable_web_page_preview=True)


@router.message(Command("about"))
async def cmd_about(message: Message) -> None:
    """Bot haqida ma'lumot."""
    await message.answer(ABOUT_TEXT, disable_web_page_preview=True)
