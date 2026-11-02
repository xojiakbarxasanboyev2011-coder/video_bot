"""
Botning kirish nuqtasi.

Ishga tushirish:
    python -m bot.main
"""

import asyncio
import logging

from aiogram import Bot

from bot.config import NOTIFY_ADMIN_ON_START, ADMIN_IDS, validate_config
from bot.handlers import main_router
from bot.instance import bot, dp, shutdown
from bot.services import cleanup_old_files
from bot.utils import setup_logging

logger = logging.getLogger(__name__)


async def _periodic_cleanup(interval_seconds: int = 10 * 60) -> None:
    """
    Har `interval_seconds` soniyada vaqtinchalik fayllarni tozalaydi.
    `dp.start_polling()` bilan parallel ishlaydi (background task).
    """
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            # cleanup_old_files sinxron — executor'da ishga tushiramiz
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, cleanup_old_files)
        except asyncio.CancelledError:
            logger.info("Cleanup task bekor qilindi.")
            return
        except Exception:
            logger.exception("Cleanup task xatosi")


async def on_startup(bot: Bot) -> None:
    """Polling boshlanishidan oldin ishga tushadi."""
    me = await bot.get_me()
    logger.info("Bot ishga tushdi: @%s (id=%s)", me.username, me.id)

    if NOTIFY_ADMIN_ON_START:
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, "✅ Bot ishga tushdi.")
            except Exception as e:
                logger.warning("Adminga xabar yuborilmadi (%s): %s", admin_id, e)


async def on_shutdown(bot: Bot) -> None:
    """Polling tugagach ishga tushadi."""
    logger.info("Bot to'xtatilmoqda...")


async def main() -> None:
    # 1) Logging'ni sozlash
    setup_logging()

    # 2) Konfiguratsiyani tekshirish (token, papkalar)
    validate_config()

    # 3) Router'larni ulash — FAQAT BIR MARTA
    dp.include_router(main_router)

    # 4) Lifecycle hook'lari
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # 5) Fon vazifasini ishga tushirish (cleanup)
    cleanup_task = asyncio.create_task(_periodic_cleanup())

    try:
        # 6) Polling — botni ishga tushirish
        # `allowed_updates` ni cheklash keraksiz yangilanishlarni filtrlaydi
        await dp.start_polling(
            bot,
            allowed_updates=["message", "callback_query"],
        )
    finally:
        # 7) To'g'ri yopish
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
        await shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Foydalanuvchi tomonidan to'xtatildi.")
