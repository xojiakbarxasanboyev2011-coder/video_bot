"""
Botning kirish nuqtasi va Render uchun Web Server.

Ishga tushirish:
    python -m bot.main
"""

import asyncio
import logging
import os
from aiohttp import web

from aiogram import Bot

from bot.config import NOTIFY_ADMIN_ON_START, ADMIN_IDS, validate_config
from bot.handlers import main_router
from bot.instance import bot, dp, shutdown
from bot.services import cleanup_old_files
from bot.utils import setup_logging

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Render uchun Health-Check server
# ─────────────────────────────────────────────────────────────
async def _start_health_server() -> None:
    """
    Render web service portni tinglashini talab qiladi.
    Bu server faqat 200 OK qaytaradi va botga xalaqit bermaydi.
    """
    async def health(request: web.Request) -> web.Response:
        return web.Response(text="OK")

    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)

    # Render avtomatik ravishda PORT muhit o'zgaruvchisini beradi
    port = int(os.getenv("PORT", "8080"))
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info("Health-check server %s-portda ishga tushdi", port)


# ─────────────────────────────────────────────────────────────
# Davriy tozalash vazifasi
# ─────────────────────────────────────────────────────────────
async def _periodic_cleanup(interval_seconds: int = 10 * 60) -> None:
    """Har 10 daqiqada vaqtinchalik fayllarni tozalaydi."""
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, cleanup_old_files)
        except asyncio.CancelledError:
            logger.info("Cleanup task bekor qilindi.")
            return
        except Exception:
            logger.exception("Cleanup task xatosi")


# ─────────────────────────────────────────────────────────────
# Lifecycle (Ishga tushish / To'xtash) hook'lari
# ─────────────────────────────────────────────────────────────
async def on_startup(bot: Bot) -> None:
    me = await bot.get_me()
    logger.info("Bot ishga tushdi: @%s (id=%s)", me.username, me.id)

    if NOTIFY_ADMIN_ON_START:
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, "✅ Bot ishga tushdi.")
            except Exception as e:
                logger.warning("Adminga xabar yuborilmadi (%s): %s", admin_id, e)


async def on_shutdown(bot: Bot) -> None:
    logger.info("Bot to'xtatilmoqda...")


# ─────────────────────────────────────────────────────────────
# Asosiy funksiya
# ─────────────────────────────────────────────────────────────
async def main() -> None:
    # 1) Logging'ni sozlash
    setup_logging()

    # 2) Konfiguratsiyani tekshirish
    validate_config()

    # 3) Router'larni ulash
    dp.include_router(main_router)

    # 4) Hook'larni ro'yxatdan o'tkazish
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # 5) Render uchun Health-check serverni ishga tushirish (Port ochish)
    await _start_health_server()

    # 6) Fon vazifasini ishga tushirish (tozalash)
    cleanup_task = asyncio.create_task(_periodic_cleanup())

    try:
        # 7) Polling — botni ishga tushirish
        await dp.start_polling(
            bot,
            allowed_updates=["message", "callback_query"],
        )
    finally:
        # 8) To'g'ri yopish
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
