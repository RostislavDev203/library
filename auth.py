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

print(sign('katana777'))


