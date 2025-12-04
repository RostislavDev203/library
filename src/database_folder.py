"""
Модуль для работы с базой данных: модели, сессии, операции с пользователями
"""
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select
from fastapi import HTTPException
import json

# Создаем асинхронный движок для работы с SQLite
# Путь к базе данных можно настроить через переменную окружения
import os
database_url = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///database.db')
engine = create_async_engine(database_url, echo=False)

# Создаем фабрику асинхронных сессий
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Model(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy"""
    pass


class User(Model):
    """
    Модель пользователя криптобиржи
    
    Attributes:
        id: Уникальный идентификатор пользователя
        login: Логин пользователя (уникальный)
        password: Хешированный пароль пользователя
        crypto: JSON строка с информацией о криптовалютах пользователя
    """
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    crypto: Mapped[str] = mapped_column(nullable=False, default='{}')  # JSON строка


async def init_db():
    """
    Инициализирует базу данных: создает все таблицы
    """
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def get_db_session():
    """
    Получает асинхронную сессию базы данных
    
    Yields:
        AsyncSession: Сессия базы данных
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_user_by_login(login: str) -> Optional[User]:
    """
    Получает пользователя по логину
    
    Args:
        login: Логин пользователя
    
    Returns:
        User | None: Пользователь или None, если не найден
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.login == login))
        return result.scalar_one_or_none()


async def get_all_users() -> list[User]:
    """
    Получает всех пользователей из базы данных
    
    Returns:
        list[User]: Список всех пользователей
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        return list(result.scalars().all())


async def create_user(login: str, password: str, crypto: dict) -> User:
    """
    Создает нового пользователя в базе данных
    
    Args:
        login: Логин пользователя
        password: Хешированный пароль
        crypto: Словарь с информацией о криптовалютах
    
    Returns:
        User: Созданный пользователь
    
    Raises:
        HTTPException: Если пользователь с таким логином уже существует
    """
    async with AsyncSessionLocal() as session:
        # Проверяем, существует ли пользователь
        existing_user = await get_user_by_login(login)
        if existing_user:
            raise HTTPException(status_code=400, detail='User with this login already exists!')
        
        # Создаем нового пользователя
        new_user = User(
            login=login,
            password=password,
            crypto=json.dumps(crypto)  # Сохраняем как JSON строку
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user


async def for_update_crypto(login: str, crypto_type: str, amount: float, operation:str):
    """
    Обновляет количество криптовалюты у пользователя
    
    Args:
        login: Логин пользователя
        crypto_type: Тип криптовалюты (BTC, ETH, USDT, XRP, BNB)
        amount: Количество для добавления (может быть отрицательным)
        operation: Тип операции (Buy, Sell)
    
    Raises:
        HTTPException: Если пользователь не найден, тип криптовалюты неизвестен, тип операции неизвестен или произошла ошибка
    """
    async with AsyncSessionLocal() as session:
        try:
            # Получаем пользователя
            result = await session.execute(select(User).where(User.login == login))
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=404, detail='User not found!')
            
            # Парсим JSON с криптовалютами
            user_crypto = json.loads(user.crypto)
            
            # Проверяем тип криптовалюты
            if crypto_type not in user_crypto:
                raise HTTPException(status_code=400, detail='Unknown type of crypto!')
            if operation == 'Buy':
             # Обновляем количество
             if 'amount' not in user_crypto[crypto_type]:
                 user_crypto[crypto_type]['amount'] = 0
             user_crypto[crypto_type]['amount'] += amount
            
             # Сохраняем обратно в базу
             user.crypto = json.dumps(user_crypto)
             await session.commit()
            elif operation == 'Sell':
             # Обновляем количество
             if 'amount' not in user_crypto[crypto_type]:
                 user_crypto[crypto_type]['amount'] = 0
             user_crypto[crypto_type]['amount'] -= amount
            else:
             raise HTTPException(status_code=401, detail='Unknown type of operation!')
            
            # Сохраняем обратно в базу
            user.crypto = json.dumps(user_crypto)
            await session.commit()

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'Something is wrong! {str(e)}')





