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
                balance INTEGER DEFAULT 0,
                vip_status INTEGER DEFAULT 0,
                vip_until TEXT,
                referrer_id INTEGER,
                referral_count INTEGER DEFAULT 0,
                registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
                last_visit TEXT DEFAULT CURRENT_TIMESTAMP,
                is_admin INTEGER DEFAULT 0
            )
        ''')
        
        # Транзакции
        await db.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                type TEXT,
                description TEXT,
                date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Скины в магазине
        await db.execute('''
            CREATE TABLE IF NOT EXISTS skins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                quality TEXT,
                price INTEGER,
                image_url TEXT,
                seller_id INTEGER,
                status TEXT DEFAULT 'available',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Сделки
        await db.execute('''
            CREATE TABLE IF NOT EXISTS deals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skin_id INTEGER,
                buyer_id INTEGER,
                seller_id INTEGER,
                price INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT
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
        # Проверяем существование
        cursor = await db.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if await cursor.fetchone():
            return
        
        # Создаём
        await db.execute('''
            INSERT INTO users (user_id, username, full_name, balance, referrer_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, full_name, 100, referrer_id))
        
        # Начисляем бонус пригласившему
        if referrer_id:
            await db.execute('''
                UPDATE users SET balance = balance + 50, referral_count = referral_count + 1
                WHERE user_id = ?
            ''', (referrer_id,))
            
            # Запись о транзакции
            await db.execute('''
                INSERT INTO transactions (user_id, amount, type, description)
                VALUES (?, ?, ?, ?)
            ''', (referrer_id, 50, 'referral_bonus', f'Бонус за реферала {user_id}'))
        
        await db.commit()
        return True

async def update_balance(user_id, amount, description=''):
    """Изменить баланс пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE users SET balance = balance + ? WHERE user_id = ?
        ''', (amount, user_id))
        
        await db.execute('''
            INSERT INTO transactions (user_id, amount, type, description)
            VALUES (?, ?, ?, ?)
        ''', (user_id, amount, 'balance_change', description))
        
        await db.commit()
        return True

async def activate_vip(user_id, days=30):
    """Активировать VIP статус"""
    vip_until = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE users SET vip_status = 1, vip_until = ? WHERE user_id = ?
        ''', (vip_until, user_id))
        await db.commit()

async def check_vip(user_id):
    """Проверить VIP статус"""
    user = await get_user(user_id)
    if not user or not user['vip_status']:
        return False
    
    if user['vip_until']:
        vip_date = datetime.strptime(user['vip_until'], '%Y-%m-%d %H:%M:%S')
        if vip_date < datetime.now():
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute('UPDATE users SET vip_status = 0 WHERE user_id = ?', (user_id,))
                await db.commit()
            return False
    return True

async def add_skin(name, quality, price, seller_id, image_url=''):
    """Добавить скин в магазин"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            INSERT INTO skins (name, quality, price, image_url, seller_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, quality, price, image_url, seller_id))
        await db.commit()
        return cursor.lastrowid

async def get_available_skins(limit=10):
    """Получить доступные скины"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('''
            SELECT * FROM skins WHERE status = 'available' ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
        return await cursor.fetchall()

async def buy_skin(skin_id, buyer_id):
    """Купить скин"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Получаем информацию о скине
        cursor = await db.execute('SELECT seller_id, price FROM skins WHERE id = ? AND status = ?', (skin_id, 'available'))
        skin = await cursor.fetchone()
        
        if not skin:
            return False, "Скин не найден"
        
        seller_id, price = skin
        
        # Проверяем баланс покупателя
        cursor = await db.execute('SELECT balance FROM users WHERE user_id = ?', (buyer_id,))
        buyer = await cursor.fetchone()
        
        if not buyer or buyer[0] < price:
            return False, "Недостаточно средств"
        
        # Создаём сделку
        await db.execute('''
            INSERT INTO deals (skin_id, buyer_id, seller_id, price, status)
            VALUES (?, ?, ?, ?, 'pending')
        ''', (skin_id, buyer_id, seller_id, price))
        
        # Обновляем статус скина
        await db.execute('UPDATE skins SET status = ? WHERE id = ?', ('sold', skin_id))
        
        # Обновляем балансы
        await db.execute('UPDATE users SET balance = balance - ? WHERE user_id = ?', (price, buyer_id))
        await db.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (price, seller_id))
        
        await db.commit()
        return True, "Покупка успешна"
