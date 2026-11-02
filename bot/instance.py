"""
Bot va Dispatcher singleton'lari.

Bu fayl `Bot` va `Dispatcher` obyektlarini BIR MARTA yaratadi.
Qolgan modullar (handler'lar, services) ularni shu yerdan import qiladi:

    from bot.instance import bot, dp

Bu yondashuv tsiklik import'ning oldini oladi:
    handlers/ → instance/ → config/
    handlers/ → services/ → config/        (instance'ga bog'liq emas)
    main.py   → instance/ + handlers/      (router'larni ulaydi)
"""

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# HTTP sessiyasi
# ─────────────────────────────────────────────────────────────
# Telegram API so'rovlari uchun timeout.
# Katta videolarni yuborish uzoq davom etishi mumkin, shuning uchun
# standart 60 s dan ancha kattaroq qiymat beramiz.
# Bu DOWNLOAD_TIMEOUT (yt-dlp uchun) bilan ARALASHTIRMASLIK kerak.
_TELEGRAM_API_TIMEOUT = 300  # soniya

_session = AiohttpSession(timeout=_TELEGRAM_API_TIMEOUT)


# ─────────────────────────────────────────────────────────────
# Bot
# ─────────────────────────────────────────────────────────────
# `DefaultBotProperties` orqali butun loyiha uchun standart
# `parse_mode` ni belgilaymiz. Shunda har bir `message.answer()` da
# `parse_mode="HTML"` yozish shart bo'lmaydi.
# `start.py`, `download.py` va boshqa handler'lar HTML teglardan
# foydalanadi — shuning uchun bu yerda global qilib qo'yamiz.

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    session=_session,
)


# ─────────────────────────────────────────────────────────────
# Dispatcher
# ─────────────────────────────────────────────────────────────
# Hozircha FSM (state machine) ishlatilmaydi, lekin `MemoryStorage`
# keyinchalik ko'p qadamli suhbatlar (masalan, "sifat tanlash")
# qo'shilganda kerak bo'ladi. Uni oldindan ulash zarar qilmaydi.
# Kelajakda Redis'ga o'tish uchun faqat shu qatorni o'zgartirasiz:
#     from aiogram.fsm.storage.redis import RedisStorage
#     dp = Dispatcher(storage=RedisStorage.from_url("redis://..."))

dp = Dispatcher(storage=MemoryStorage())


# ─────────────────────────────────────────────────────────────
# Tozalash (shutdown)
# ─────────────────────────────────────────────────────────────

async def shutdown() -> None:
    """
    Botni to'g'ri yopadi.

    `main.py` da `dp.start_polling()` tugagach chaqiriladi.
    Sessiya yopilmasa, aiohttp "Unclosed client session" ogohlantirishi
    chiqadi va resurslar bo'shatilmaydi.
    """
    logger.info("Bot sessiyasi yopilmoqda...")
    await bot.session.close()
    logger.info("Sessiya yopildi.")


# ─────────────────────────────────────────────────────────────
# Debug: `python -m bot.instance` bilan obyektlarni tekshirish
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Instance holati ===")
    print(f"Bot yaratildi     : @{(bot.username or 'noma`lum')}")
    print(f"Parse mode        : {bot.default.parse_mode}")
    print(f"API timeout       : {_TELEGRAM_API_TIMEOUT} s")
    print(f"Dispatcher storage: {type(dp.storage).__name__}")
