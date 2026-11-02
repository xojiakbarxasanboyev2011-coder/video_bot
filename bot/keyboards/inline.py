"""
Inline klaviaturalar.

Har bir funksiya tayyor InlineKeyboardMarkup qaytaradi.
Handler'lar bu funksiyalarni chaqirib, xabarga biriktiradi.
"""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def help_keyboard() -> InlineKeyboardMarkup:
    """
    /start xabariga biriktiriladigan asosiy menyu.
    Foydalanuvchi qo'llanma yoki bot haqida ma'lumot olishi mumkin.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="📖 Qo'llanma", callback_data="show_help")
    builder.button(text="ℹ️ Bot haqida", callback_data="show_about")
    builder.adjust(2)  # ikkita tugma bir qatorda
    return builder.as_markup()


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Qo'llanma yoki "Bot haqida" sahifasidan asosiy menyuga qaytish uchun.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Orqaga", callback_data="back_to_start")
    return builder.as_markup()


def after_download_keyboard() -> InlineKeyboardMarkup:
    """
    Video muvaffaqiyatli yuborilgandan keyin ko'rsatiladigan tugmalar.
    Foydalanuvchini yana video yuborishga undaydi.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="🎬 Yana video yuklash", callback_data="new_download")
    builder.button(text="❓ Yordam", callback_data="show_help")
    builder.adjust(1)  # har bir tugma alohida qatorda
    return builder.as_markup()
