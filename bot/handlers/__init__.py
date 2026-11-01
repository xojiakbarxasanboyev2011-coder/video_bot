"""
Handlers paketi.

Bu fayl barcha handler modullaridan router'larni yig'adi va
yagona `main_router` obyektini eksport qiladi.

Foydalanish (bot/main.py da):
    from bot.handlers import main_router
    dp.include_router(main_router)
"""

from aiogram import Router

from .start import router as start_router
from .download import router as download_router

# Barcha router'larni bitta asosiy router ostida birlashtiramiz
main_router = Router(name="main_router")

# Tartib muhim: birinchi qo'shilgan router birinchi tekshiriladi.
# /start va /help kabi buyruqlar birinchi turishi kerak,
# aks holda "catch-all" handler ularni ushlab qolishi mumkin.
main_router.include_router(start_router)
main_router.include_router(download_router)

# Faqat `main_router` ni eksport qilamiz — bu paketning public API'si
__all__ = ["main_router"]
