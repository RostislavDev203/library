"""
Модуль для работы с JWT токенами: создание и декодирование токенов
"""
import jwt
from fastapi import HTTPException
from utils import JWT_SECRET_KEY

# Алгоритм для подписи JWT токенов
JWT_ALGORITHM = 'HS256'


def sign(login: str) -> str:
    """
    Создает JWT токен для пользователя
    
    Args:
        login: Логин пользователя
    
    Returns:
        str: JWT токен
    """
    payload = {
        'login': login
    }
    token = jwt.encode(payload, key=JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def decode(token: str) -> dict:
    """
    Декодирует JWT токен и возвращает данные пользователя
    
    Args:
        token: JWT токен для декодирования
    
    Returns:
        dict: Данные из токена (например, {'login': 'username'})
    
    Raises:
        HTTPException: Если токен невалидный, истек или не может быть декодирован
    """
    try:
        decoded_token = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token has expired!')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token!')
    except Exception as e:
        raise HTTPException(status_code=401, detail=f'Token decoding error: {str(e)}')


