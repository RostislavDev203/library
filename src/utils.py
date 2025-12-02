"""
Утилиты для криптобиржи: работа с ценами криптовалют, аутентификация пользователей
"""
import secrets
import bcrypt
import httpx
from database import get_user_by_login, create_user, get_all_users, User
from fastapi import HTTPException, WebSocket
from auth import sign
from router_file import home

# URL API для получения цен криптовалют
url = 'https://api.coingecko.com/api/v3/simple/price'

# Секретный ключ для JWT токенов
JWT_SECRET_KEY = secrets.token_hex(16)

# Словарь для хранения информации о криптовалютах
cryptos = {
    'BTC': {'price': None, 'amount': 0},
    'ETH': {'price': None, 'amount': 0},
    'USDT': {'price': None, 'amount': 0},
    'XRP': {'price': None, 'amount': 0},
    'BNB': {'price': None, 'amount': 0}
}

# Соль для хеширования паролей
salt = bcrypt.gensalt()


async def fetch_crypto_price(crypto_id: str) -> dict:
    """
    Получает текущую цену криптовалюты из API CoinGecko
    
    Args:
        crypto_id: ID криптовалюты в CoinGecko (например, 'bitcoin', 'ethereum')
    
    Returns:
        dict: Словарь с ценой и изменением за 24 часа
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                params={
                    'ids': crypto_id,
                    'vs_currencies': 'usd',
                    'include24hr_change': 'true'
                },
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f'Failed to fetch crypto price: {str(e)}')


async def update_crypto_prices():
    """
    Обновляет цены всех криптовалют в словаре cryptos
    """
    try:
        btc_data = await fetch_crypto_price('bitcoin')
        eth_data = await fetch_crypto_price('ethereum')
        usdt_data = await fetch_crypto_price('tether')
        xrp_data = await fetch_crypto_price('ripple')
        bnb_data = await fetch_crypto_price('binancecoin')
        
        cryptos['BTC']['price'] = btc_data.get('bitcoin', {})
        cryptos['ETH']['price'] = eth_data.get('ethereum', {})
        cryptos['USDT']['price'] = usdt_data.get('tether', {})
        cryptos['XRP']['price'] = xrp_data.get('ripple', {})
        cryptos['BNB']['price'] = bnb_data.get('binancecoin', {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error updating crypto prices: {str(e)}')


@home.websocket('/')
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint для передачи обновлений цен криптовалют в реальном времени
    
    Args:
        websocket: WebSocket соединение
    """
    await websocket.accept()
    try:
        while True:
            # Обновляем цены криптовалют
            await update_crypto_prices()
            # Отправляем обновленные данные клиенту
            await websocket.send_json(cryptos)
            # Ждем перед следующим обновлением (например, 5 секунд)
            import asyncio
            await asyncio.sleep(5)
    except Exception as e:
        await websocket.send_json({'error': str(e)})
    finally:
        await websocket.close()


async def create_new_user(login: str, password: str, cryptomoney: dict = None):
    """
    Создает нового пользователя в системе
    
    Args:
        login: Логин пользователя
        password: Пароль пользователя (будет захеширован)
        cryptomoney: Словарь с криптовалютами пользователя (опционально)
    
    Returns:
        User: Созданный пользователь
    
    Raises:
        HTTPException: Если пользователь с таким логином уже существует
    """
    # Проверяем, существует ли пользователь
    existing_user = await get_user_by_login(login)
    if existing_user:
        raise HTTPException(status_code=400, detail='User with this login already exists!')
    
    # Хешируем пароль
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    # Если cryptomoney не указан, используем пустой словарь
    if cryptomoney is None:
        cryptomoney = {crypto: {'amount': 0} for crypto in cryptos.keys()}
    
    # Создаем нового пользователя
    new_user = await create_user(login=login, password=hashed_password.decode('utf-8'), crypto=cryptomoney)
    return new_user


async def authentification(login: str, password: str) -> str:
    """
    Аутентифицирует пользователя по логину и паролю
    
    Args:
        login: Логин пользователя
        password: Пароль пользователя
    
    Returns:
        str: JWT токен для аутентифицированного пользователя
    
    Raises:
        HTTPException: Если логин или пароль неверны
    """
    # Получаем пользователя из базы данных
    user = await get_user_by_login(login)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid login or password!')
    
    # Проверяем пароль
    if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        # Генерируем JWT токен
        new_sign = sign(login=login)
        return new_sign
    else:
        raise HTTPException(status_code=401, detail='Invalid login or password!')

