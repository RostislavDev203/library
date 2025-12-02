"""
Главный файл приложения криптобиржи
Инициализирует FastAPI приложение и подключает все роутеры
"""
from router_file import auth, home, buycrypto, sellcrypto
from fastapi import FastAPI
from database import init_db
import asyncio

# Создаем экземпляр FastAPI приложения
app = FastAPI(
    title="Cryptocurrency Exchange API",
    description="API для криптобиржи с поддержкой аутентификации и покупки криптовалют",
    version="1.0.0"
)

# Подключаем роутеры
app.include_router(auth)
app.include_router(home)
app.include_router(buycrypto)
app.include_router(sellcrypto)


@app.on_event("startup")
async def startup_event():
    """
    Событие запуска приложения: инициализирует базу данных
    """
    await init_db()


@app.get("/")
async def root():
    """
    Корневой endpoint API
    
    Returns:
        dict: Приветственное сообщение
    """
    return {
        "message": "Welcome to Cryptocurrency Exchange API",
        "docs": "/docs",
        "version": "1.0.0"
    }

