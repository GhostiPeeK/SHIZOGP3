import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

# Загружаем переменные окружения (для локального теста, на BotHost не обязательно)
load_dotenv()

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("❌ НЕТ ТОКЕНА! Добавьте BOT_TOKEN в переменные окружения BotHost")

# ========== ИНИЦИАЛИЗАЦИЯ ==========
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# ========== КОМАНДЫ ==========
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"🔥 **SHIZOGP БОТ РАБОТАЕТ!**\n"
        f"🆔 Твой ID: `{message.from_user.id}`\n"
        f"🌐 Хостинг: BotHost\n"
        f"✅ Версия: 1.0",
        parse_mode="Markdown"
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📋 **Доступные команды:**\n\n"
        "/start - Начать работу\n"
        "/help - Показать помощь\n"
        "/info - Информация о боте\n"
        "/balance - Проверить баланс\n"
        "/referral - Реферальная ссылка",
        parse_mode="Markdown"
    )

@dp.message(Command("info"))
async def cmd_info(message: Message):
    await message.answer(
        f"🤖 **Информация о боте:**\n\n"
        f"Название: SHIZOGP\n"
        f"Версия: 1.0\n"
        f"Платформа: Telegram\n"
        f"Хостинг: BotHost\n"
        f"Библиотека: aiogram 3.4.1",
        parse_mode="Markdown"
    )

@dp.message(Command("balance"))
async def cmd_balance(message: Message):
    await message.answer(
        f"💰 **Твой баланс:**\n\n"
        f"Монеты: `100` 🪙\n"
        f"(Тестовый режим)",
        parse_mode="Markdown"
    )

@dp.message(Command("referral"))
async def cmd_referral(message: Message):
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{message.from_user.id}"
    
    await message.answer(
        f"🤝 **Реферальная программа:**\n\n"
        f"Твоя ссылка:\n`{ref_link}`\n\n"
        f"Приглашай друзей и получай бонусы!",
        parse_mode="Markdown"
    )

@dp.message()
async def echo_message(message: Message):
    """Отвечает на любое сообщение"""
    await message.answer(f"Ты написал: {message.text}\n\nИспользуй /help для списка команд.")

# ========== ЗАПУСК ==========
async def main():
    print("🔥 SHIZOGP БОТ УСПЕШНО ЗАПУЩЕН!")
    print(f"🤖 Бот: @{(await bot.get_me()).username}")
    print(f"🆔 ID: {BOT_TOKEN.split(':')[0]}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())