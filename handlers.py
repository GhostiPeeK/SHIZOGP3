from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from datetime import datetime

from bot.database import get_user, create_user
from bot.keyboards import get_main_keyboard, get_back_keyboard, get_vip_keyboard

router = Router()
VIP_CHAT_LINK = "https://t.me/+r3rxYlBjbTYyMDY6"

# ========== КОМАНДА СТАРТ ==========
@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "NoName"
    full_name = message.from_user.full_name
    
    # Парсим реферала
    args = message.text.split()
    referrer_id = None
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].replace("ref_", ""))
            if referrer_id == user_id:
                referrer_id = None
        except:
            pass
    
    await create_user(user_id, username, full_name, referrer_id)
    
    await message.answer(
        f"👋 Добро пожаловать в **SHIZOGP**!\n\n"
        f"Выбери действие в меню ниже:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

# ========== КОМАНДА МЕНЮ ==========
@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(
        "📋 **Главное меню**\nВыбери действие:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

# ========== КОМАНДА ПОМОЩЬ ==========
@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "ℹ️ **Доступные команды:**\n\n"
        "/start - Запустить бота\n"
        "/menu - Открыть меню\n"
        "/help - Показать помощь\n\n"
        "Или используй кнопки в меню!",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

# ========== ВОЗВРАТ В МЕНЮ ==========
@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "📋 **Главное меню**\nВыбери действие:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

# ========== БАЛАНС ==========
@router.callback_query(F.data == "balance")
async def show_balance(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    balance = user['balance'] if user else 100
    
    await callback.message.edit_text(
        f"💰 **ТВОЙ БАЛАНС**\n\n"
        f"Монет: **{balance}** 💰\n\n"
        f"Пополнить баланс можно через рефералов: /referral",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )

# ========== РЕФЕРАЛЫ ==========
@router.callback_query(F.data == "referral")
async def show_referral(callback: CallbackQuery):
    user_id = callback.from_user.id
    bot_info = await callback.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
    
    user = await get_user(user_id)
    referrals = user['referral_count'] if user else 0
    
    await callback.message.edit_text(
        f"🤝 **РЕФЕРАЛЬНАЯ ПРОГРАММА**\n\n"
        f"Твоих рефералов: **{referrals}**\n"
        f"Бонус за друга: **50 монет**\n\n"
        f"🔗 Твоя ссылка:\n`{ref_link}`\n\n"
        f"Отправь её друзьям и получай бонусы!",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )

# ========== VIP ==========
@router.callback_query(F.data == "vip")
async def show_vip(callback: CallbackQuery):
    await callback.message.edit_text(
        "👑 **VIP СТАТУС**\n\n"
        "VIP даёт доступ к закрытому чату и эксклюзивным предложениям.\n\n"
        "💰 Стоимость: **550 монет**\n"
        "📅 Длительность: **30 дней**",
        reply_markup=get_vip_keyboard(False),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "buy_vip")
async def buy_vip(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    balance = user['balance'] if user else 100
    
    if balance >= 550:
        await callback.message.edit_text(
            f"✅ **VIP АКТИВИРОВАН!**\n\n"
            f"Тебе доступен закрытый VIP чат!\n"
            f"Ссылка: {VIP_CHAT_LINK}",
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )
    else:
        need = 550 - balance
        await callback.message.edit_text(
            f"❌ Недостаточно монет.\n\n"
            f"Тебе нужно ещё **{need}** монет.\n"
            f"Приглашай друзей по реферальной ссылке!",
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )

# ========== ПРОФИЛЬ ==========
@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    
    if not user:
        await callback.message.edit_text(
            "❌ Пользователь не найден",
            reply_markup=get_back_keyboard()
        )
        return
    
    text = f"📊 **ТВОЙ ПРОФИЛЬ**\n\n"
    text += f"🆔 ID: `{user_id}`\n"
    text += f"👤 Имя: {user['full_name']}\n"
    text += f"💰 Баланс: {user['balance']} монет\n"
    text += f"👥 Рефералов: {user['referral_count']}\n"
    text += f"👑 VIP: {'✅' if user['vip_status'] else '❌'}\n"
    text += f"📅 Регистрация: {user['registration_date'][:10]}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )

# ========== МАГАЗИН ==========
@router.callback_query(F.data == "shop")
async def show_shop(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛒 **МАГАЗИН**\n\n"
        "Магазин временно пуст.\n"
        "Скоро здесь появятся скины!",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )

# ========== ПОМОЩЬ ==========
@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ **ПОМОЩЬ**\n\n"
        "📌 **Доступные команды:**\n"
        "/start - Запустить бота\n"
        "/menu - Открыть меню\n"
        "/help - Показать помощь\n\n"
        "📌 **Разделы меню:**\n"
        "🛒 Магазин - покупка скинов\n"
        "💰 Баланс - проверка средств\n"
        "🤝 Рефералы - приглашай друзей\n"
        "👑 VIP - закрытый чат\n"
        "📊 Профиль - твои данные",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )

# ========== ТЕКСТОВЫЕ СООБЩЕНИЯ ==========
@router.message()
async def handle_text(message: Message):
    await message.answer(
        "Используй команду /menu или кнопки в меню!",
        reply_markup=get_main_keyboard()
    )
