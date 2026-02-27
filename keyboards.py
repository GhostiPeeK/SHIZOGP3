from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_keyboard():
    """Главное меню"""
    buttons = [
        [InlineKeyboardButton(text="🛒 Магазин", callback_data="shop")],
        [
            InlineKeyboardButton(text="💰 Баланс", callback_data="balance"),
            InlineKeyboardButton(text="🤝 Рефералы", callback_data="referral")
        ],
        [
            InlineKeyboardButton(text="👑 VIP", callback_data="vip"),
            InlineKeyboardButton(text="📊 Профиль", callback_data="profile")
        ],
        [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_keyboard():
    """Кнопка назад"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀ Назад в меню", callback_data="main_menu")]
    ])

def get_vip_keyboard(is_vip=False):
    """Клавиатура для VIP"""
    if is_vip:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👑 VIP чат", url="https://t.me/+r3rxYlBjbTYyMDY6")],
            [InlineKeyboardButton(text="◀ Назад", callback_data="main_menu")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💎 Купить VIP (550💰)", callback_data="buy_vip")],
            [InlineKeyboardButton(text="◀ Назад", callback_data="main_menu")]
        ])
