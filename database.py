import aiosqlite
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

async def init_db():
    """Создание всех таблиц"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Пользователи
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                balance INTEGER DEFAULT 100,
                vip_status INTEGER DEFAULT 0,
                vip_until TEXT,
                referrer_id INTEGER,
                referral_count INTEGER DEFAULT 0,
                registration_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

async def get_user(user_id):
    """Получить данные пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        return await cursor.fetchone()

async def create_user(user_id, username, full_name, referrer_id=None):
    """Создать нового пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if await cursor.fetchone():
            return
        
        await db.execute('''
            INSERT INTO users (user_id, username, full_name, balance, referrer_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, full_name, 100, referrer_id))
        
        if referrer_id:
            await db.execute('''
                UPDATE users SET balance = balance + 50, referral_count = referral_count + 1
                WHERE user_id = ?
            ''', (referrer_id,))
        
        await db.commit()
        return True
        
        await db.commit()
        return True, "Покупка успешна"
