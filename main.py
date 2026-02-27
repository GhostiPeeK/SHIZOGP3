#!/usr/bin/env python3
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import router
from bot.database import init_db
from bot.config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if not BOT_TOKEN:
    logger.error("❌ Нет токена! Добавь BOT_TOKEN в .env")
    exit(1)

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

async def on_startup():
    logger.info("🚀 Запуск SHIZOGP...")
    await init_db()
    logger.info("✅ База данных готова")
    me = await bot.get_me()
    logger.info(f"✅ Бот: @{me.username}")

async def on_shutdown():
    logger.info("👋 Бот остановлен")

async def main():
    await on_startup()
    try:
        logger.info("🔥 Бот запущен и готов к работе!")
        await dp.start_polling(bot)
    finally:
        await on_shutdown()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
