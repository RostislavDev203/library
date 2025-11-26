import jwt
from fastapi import HTTPException
from .utils import JWT_SECRET_KEY

JWT_ALGORITHM = 'HS256'

def sign(login:str):
    payload = {
        'login': login
    }
    token = jwt.encode(payload, key=JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def decode(token)->dict:
    try:
        decoded_token = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return decoded_token
    except:
        raise HTTPException(status_code=401, detail='Ivalid token')


