import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from bot.keyboards import back_to_menu_keyboard, help_keyboard

logger = logging.getLogger(__name__)
router = Router(name="start_router")


# ─────────────────────────────────────────────────────────────
# Matnlar — bitta joyda saqlash osonroq (kelajakda i18n uchun qulay)
# ─────────────────────────────────────────────────────────────

WELCOME_TEXT = (
    "👋 <b>What's uppppp, {name}!</b>\n\n"
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
    "Yana men ochiq kodli xavfsiz dasutur xisoblanaman. Meni GitHub dan topishingiz mumkin!"
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


# ─────────────────────────────────────────────────────────────
# Buyruqlar
# ─────────────────────────────────────────────────────────────

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
    """Foydalanuvchi /help bosganda batafsil qo'llanmani ko'rsatadi."""
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


# ─────────────────────────────────────────────────────────────
# Callback handler'lar
# ─────────────────────────────────────────────────────────────

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
