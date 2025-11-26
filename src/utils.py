import secrets, bcrypt, random
from .database import session, users, User
from fastapi import HTTPException
from .auth import sign

JWT_SECRET_KEY = secrets.token_hex(16)

cryptos = {
           'BTC': {'price':0, 'amount':0}, 
           'ETH': {'price':0, 'amount':0}, 
           'USDT': {'price':0, 'amount':0}, 
           'XRP': {'price':0, 'amount':0}, 
           'BNB': {'price':0, 'amount':0}
           }

salt = bcrypt.gensalt()

def create_new_user(login:str, password:str, cryptomoney:dict):
    for user in users:
        if user.login == login:
            raise HTTPException(status_code=401, detail='This login is already taken!')
        else:
            continue
    try:
        session.add(User(id=random.randint(1, 9999999999), login=login, password=bcrypt.hashpw(password, salt=salt), cryptomoney=cryptos))
        session.commit()
        raise HTTPException(status_code=201, detail='Successful creating!')
    except:
        raise HTTPException(status_code=500, detail='Something is wrong, try later!')
    

def authentification(login:str, password:str):
    for user in users:
        if bcrypt.checkpw(password, user.password):
            new_sign = sign(login=login)
            return new_sign
        else:
            raise HTTPException(status_code=401, detail='Invalid login or password!')

