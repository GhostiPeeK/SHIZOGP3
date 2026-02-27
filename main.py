#!/usr/bin/env python3
import asyncio
import logging
import os
import sys

# Добавляем путь к папке проекта
sys.path.append(os.path.dirname(__file__))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Теперь импортируем из папки bot
from bot.handlers import router
from bot.database import init_db

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфиг
BOT_TOKEN = os.getenv('BOT_TOKEN')

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
    logger.info("🔥 Бот запущен и готов к работе!")

async def on_shutdown():
    logger.info("👋 Бот остановлен")

async def main():
    await on_startup()
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
