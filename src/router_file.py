"""
Роутеры для API криптобиржи: аутентификация, главная страница, покупка криптовалют
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from utils import create_new_user, authentification, cryptos, update_crypto_prices
from auth import decode
from database import for_update_crypto
from typing import Annotated

# Роутер для аутентификации
auth = APIRouter(prefix='/auth', tags=["Auth"])


class AuthData(BaseModel):
    """Модель данных для аутентификации"""
    login: str
    password: str


class BuyData(BaseModel):
    """Модель данных для покупки криптовалюты"""
    token: str
    type: str
    amount: float


@auth.post('/sign-in')
async def sign_in(authdata: Annotated[AuthData, Depends()]):
    """
    Регистрация нового пользователя
    
    Args:
        authdata: Данные для регистрации (логин и пароль)
    
    Returns:
        dict: Сообщение об успешной регистрации
    
    Raises:
        HTTPException: Если пользователь с таким логином уже существует
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
    
    Args:
        authdata: Данные для входа (логин и пароль)
    
    Returns:
        dict: JWT токен для аутентифицированного пользователя
    
    Raises:
        HTTPException: Если логин или пароль неверны
    """
    try:
        token = await authentification(authdata.login, authdata.password)
        return {'token': token}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error during authentication: {str(e)}')


# Роутер для главной страницы
home = APIRouter(prefix='/home', tags=["Home"])


@home.get('/main')
async def main_page():
    """
    Получает текущие цены всех криптовалют
    
    Returns:
        dict: Словарь с ценами криптовалют
    """
    # Обновляем цены перед возвратом
    await update_crypto_prices()
    return {
        'BTC': cryptos['BTC']['price'],
        'ETH': cryptos['ETH']['price'],
        'USDT': cryptos['USDT']['price'],
        'XRP': cryptos['XRP']['price'],
        'BNB': cryptos['BNB']['price']
    }


# Роутер для покупки криптовалют
buycrypto = APIRouter(prefix='/buycrypto', tags=["Buycrypto"])


@buycrypto.post('/')
async def buy_crypto(buydata: Annotated[BuyData, Depends()]):
    """
    Покупка криптовалюты пользователем
    
    Args:
        buydata: Данные для покупки (токен, тип криптовалюты, количество)
    
    Returns:
        dict: Сообщение об успешной покупке
    
    Raises:
        HTTPException: Если токен невалидный, тип криптовалюты неизвестен или произошла ошибка
    """
    try:
        # Декодируем токен для получения логина пользователя
        info = decode(buydata.token)
        
        # Обновляем количество криптовалюты у пользователя
        await for_update_crypto(info['login'], buydata.type, buydata.amount, 'Buy')
        
        return {'message': f'Successfully updated {buydata.type} amount by {buydata.amount}'}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error buying crypto: {str(e)}')
    
# Роутер для продажи криптовалют
sellcrypto = APIRouter(prefix='/sellcrypto')

@sellcrypto.post('/')
async def sell_crypto(selldata: Annotated[BuyData, Depends()]):
    """
    Продажа криптовалюты пользователя

    Args:
        selldata: Данные для продажи (токен, тип криптовалюты, количество)

    Returns:
        dict: Сообщение об успешной продаже

    Raises:
        HTTPException: Если токен невалидный, тип криптовалюты неизвестен или произошла ошибка
    """
    try:
        # Декодируем токен для получения логина пользователя
        info = decode(selldata.token)

        # Обновляем количество криптовалюты у пользователя
        await for_update_crypto(info['login'], selldata.type, selldata.amount, 'Sell')

        return {'message': f'Successfully updated {selldata.type} amount by {selldata.amount}'}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error selling crypto: {str(e)}')