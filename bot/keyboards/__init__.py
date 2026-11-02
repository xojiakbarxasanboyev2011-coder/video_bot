"""
Keyboards paketi.

Barcha inline va reply klaviaturalarni yagona joydan eksport qiladi.

Foydalanish:
    from bot.keyboards import help_keyboard, back_to_menu_keyboard
"""

from .inline import (
    help_keyboard,
    back_to_menu_keyboard,
    after_download_keyboard,
)

__all__ = [
    "help_keyboard",
    "back_to_menu_keyboard",
    "after_download_keyboard",
]
