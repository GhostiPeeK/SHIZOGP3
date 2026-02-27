from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from bot.database import *
from bot.keyboards import *
from bot.config import VIP_CHAT_LINK, VIP_PRICE

router = Router()

class ShopStates(StatesGroup):
    waiting_for_skin_name = State()
    waiting_for_skin_quality = State()
    waiting_for_skin_price = State()

# ========== СТАРТ ==========
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
    user = await get_user(user_id)
    
    await message.answer(
        f"👋 Добро пожаловать в **SHIZOGP**!\n\n"
        f"💰 Баланс: **{user['balance']}** монет\n"
        f"👑 VIP: {'✅' if await check_vip(user_id) else '❌'}\n"
        f"🤝 Рефералов: **{user['referral_count']}**\n\n"
        f"Выбери действие в меню:",
        reply_markup=get_main_keyboard(VIP_CHAT_LINK),
        parse_mode="Markdown"
    )

# ========== БАЛАНС ==========
@router.callback_query(F.data == "balance")
async def show_balance(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    
    await callback.message.edit_text(
        f"💰 **ТВОЙ БАЛАНС**\n\n"
        f"Монет: **{user['balance']}** 💰\n"
        f"Рефералов: **{user['referral_count']}** 👥\n"
        f"VIP статус: {'✅' if await check_vip(callback.from_user.id) else '❌'}\n\n"
        f"Пополнить баланс можно через рефералов или купив VIP.",
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
    
    await callback.message.edit_text(
        f"🤝 **РЕФЕРАЛЬНАЯ ПРОГРАММА**\n\n"
        f"Твоих рефералов: **{user['referral_count']}**\n"
        f"Бонус за друга: **50 монет**\n\n"
        f"🔗 Твоя ссылка:\n`{ref_link}`\n\n"
        f"Отправь её друзьям и получай бонусы!",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )

# ========== VIP ==========
@router.callback_query(F.data == "vip_chat")
async def vip_chat(callback: CallbackQuery):
    if await check_vip(callback.from_user.id):
        await callback.message.edit_text(
            f"👑 **VIP ЧАТ**\n\n"
            f"Ссылка для входа:\n{VIP_CHAT_LINK}",
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            "❌ У тебя нет VIP статуса.\n\n"
            "Купи VIP за 550 монет, чтобы получить доступ к закрытому чату!",
            reply_markup=get_vip_keyboard(False),
            parse_mode="Markdown"
        )

@router.callback_query(F.data == "buy_vip")
async def buy_vip(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    
    if user['balance'] >= 550:
        await update_balance(user_id, -550, 'Покупка VIP')
        await activate_vip(user_id)
        
        await callback.message.edit_text(
            f"✅ **VIP АКТИВИРОВАН!**\n\n"
            f"Тебе доступен закрытый VIP чат!\n"
            f"Ссылка: {VIP_CHAT_LINK}",
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )
    else:
        need = 550 - user['balance']
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
    
    # Получаем историю транзакций
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
            SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC LIMIT 5
        ''', (user_id,))
        transactions = await cursor.fetchall()
    
    text = f"📊 **ТВОЙ ПРОФИЛЬ**\n\n"
    text += f"🆔 ID: `{user_id}`\n"
    text += f"👤 Имя: {user['full_name']}\n"
    text += f"💰 Баланс: {user['balance']} монет\n"
    text += f"👥 Рефералов: {user['referral_count']}\n"
    text += f"👑 VIP: {'✅' if await check_vip(user_id) else '❌'}\n"
    text += f"📅 Регистрация: {user['registration_date'][:10]}\n\n"
    
    if transactions:
        text += "📝 Последние операции:\n"
        for t in transactions:
            emoji = "➕" if t['amount'] > 0 else "➖"
            text += f"{emoji} {t['description']}: {t['amount']}💰\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )

# ========== МАГАЗИН ==========
@router.callback_query(F.data == "shop")
async def show_shop(callback: CallbackQuery):
    skins = await get_available_skins(5)
    
    if not skins:
        await callback.message.edit_text(
            "🛒 **МАГАЗИН**\n\nПока нет доступных скинов.",
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )
        return
    
    await callback.message.edit_text(
        "🛒 **Доступные скины:**\n\nВыбери скин для покупки:",
        reply_markup=get_shop_keyboard(skins),
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("buy_"))
async def buy_skin_handler(callback: CallbackQuery):
    skin_id = int(callback.data.replace("buy_", ""))
    buyer_id = callback.from_user.id
    
    success, message = await buy_skin(skin_id, buyer_id)
    
    if success:
        await callback.message.edit_text(
            f"✅ {message}\n\nСкин скоро будет отправлен продавцом.",
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            f"❌ {message}",
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )

# ========== ПОМОЩЬ ==========
@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ **ПОМОЩЬ**\n\n"
        "📌 **Доступные команды:**\n"
        "/start - Главное меню\n\n"
        "📌 **Разделы:**\n"
        "🛒 Магазин - покупка скинов\n"
        "💰 Баланс - проверка средств\n"
        "🤝 Рефералы - приглашай друзей\n"
        "👑 VIP - закрытый чат\n"
        "📊 Профиль - твои данные\n\n"
        "❓ Вопросы? Пиши @support",
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )

# ========== НАЗАД ==========
@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user(user_id)
    
    await callback.message.edit_text(
        f"👋 Главное меню\n\n"
        f"💰 Баланс: **{user['balance']}** монет",
        reply_markup=get_main_keyboard(VIP_CHAT_LINK),
        parse_mode="Markdown"
    )

# ========== ТЕКСТОВЫЕ СООБЩЕНИЯ ==========
@router.message()
async def handle_text(message: Message):
    await message.answer(
        "Используй кнопки меню или команду /start",
        reply_markup=get_main_keyboard(VIP_CHAT_LINK)
    )
