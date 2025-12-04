"""
Роутеры для API криптобиржи: аутентификация, главная страница, покупка и продажа криптовалют, WebSocket
"""
from typing import Annotated
import asyncio

from fastapi import APIRouter, HTTPException, Depends, WebSocket
from pydantic import BaseModel

from .utils import create_new_user, authentification, cryptos, update_crypto_prices
from .auth_folder import decode
from .database_folder import for_update_crypto

# Роутер для аутентификации
auth = APIRouter(prefix='/auth', tags=["Auth"])


class AuthData(BaseModel):
    """Модель данных для аутентификации"""
    login: str
    password: str


class BuyData(BaseModel):
    """Модель данных для покупки/продажи криптовалюты"""
    token: str
    type: str
    amount: float


@auth.post('/sign-in')
async def sign_in(authdata: Annotated[AuthData, Depends()]):
    """
    Регистрация нового пользователя
    """
    try:
        await create_new_user(login=authdata.login, password=authdata.password)
        return {'message': 'User created successfully!'}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error creating user: {str(e)}')


@auth.post('/log-in')
async def log_in(authdata: Annotated[AuthData, Depends()]):
    """
    Вход пользователя в систему
    """
    try:
        token = await authentification(authdata.login, authdata.password)
        return {'token': token}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error during authentication: {str(e)}')


# Роутер для главной страницы и WebSocket
home = APIRouter(prefix='/home', tags=["Home"])


@home.get('/main')
async def main_page():
    """
    Получает текущие цены всех криптовалют
    """
    await update_crypto_prices()
    return {
        'BTC': cryptos['BTC']['price'],
        'ETH': cryptos['ETH']['price'],
        'USDT': cryptos['USDT']['price'],
        'XRP': cryptos['XRP']['price'],
        'BNB': cryptos['BNB']['price']
    }


@home.websocket('/')
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint для передачи обновлений цен криптовалют в реальном времени
    """
    await websocket.accept()
    try:
        while True:
            # Обновляем цены криптовалют
            await update_crypto_prices()
            # Отправляем обновленные данные клиенту
            await websocket.send_json(cryptos)
            # Ждем перед следующим обновлением (например, 5 секунд)
            await asyncio.sleep(5)
    except Exception as e:
        await websocket.send_json({'error': str(e)})
    finally:
        await websocket.close()


# Роутер для покупки криптовалют
buycrypto = APIRouter(prefix='/buycrypto', tags=["Buycrypto"])


@buycrypto.post('/')
async def buy_crypto(buydata: Annotated[BuyData, Depends()]):
    """
    Покупка криптовалюты пользователем
    """
    try:
        info = decode(buydata.token)
        await for_update_crypto(info['login'], buydata.type, buydata.amount, 'Buy')
        return {'message': f'Successfully updated {buydata.type} amount by {buydata.amount}'}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error buying crypto: {str(e)}')


# Роутер для продажи криптовалют
sellcrypto = APIRouter(prefix='/sellcrypto', tags=["Sellcrypto"])


@sellcrypto.post('/')
async def sell_crypto(selldata: Annotated[BuyData, Depends()]):
    """
    Продажа криптовалюты пользователя
    """
    try:
        info = decode(selldata.token)
        await for_update_crypto(info['login'], selldata.type, selldata.amount, 'Sell')
        return {'message': f'Successfully updated {selldata.type} amount by {selldata.amount}'}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error selling crypto: {str(e)}')