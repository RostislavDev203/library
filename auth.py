import jwt
import secrets
from fastapi import HTTPException

JWT_SECRET_KEY = secrets.token_hex(16)
JWT_ALGORITHM = 'HS256'

def sign(login:str):
    payload = {
        'login': login
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return token

def decode(token):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

        return decoded_token
    except:
        raise HTTPException(status_code=401, detail='Ivalid token')


