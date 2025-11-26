from fastapi import APIRouter, WebSocket
from pydantic import BaseModel
from .utils import create_new_user, authentification, cryptos
from .auth import decode
from .database import for_update_crypto, session

auth = APIRouter(prefix='/auth', tags=["Auth"])

class AuthData(BaseModel):
    login:str
    password:str

class BuyData(BaseModel):
    token:str
    type:str
    amount:int

@auth.post('/sign-in')
async def sign_in(authdata:AuthData):
    await create_new_user(login=authdata.login, password=authdata.password)
    

@auth.post('/log-in')
async def log_in(authdata:AuthData):
    await authentification(authdata.login, authdata.password)

home = APIRouter(prefix='/home', tags=["Home"])

@home.get('/main')
async def main_page():
    return {
           'BTC': cryptos['BTC'['price']], 
           'ETH': cryptos['ETH'['price']], 
           'USDT': cryptos['USDT'['price']], 
           'XRP': cryptos['XRP'['price']], 
           'BNB': cryptos['BNB'['price']]
           }

buycrypto = APIRouter(prefix='/auth', tags=["Buycrypto"])

@buycrypto.post('/buycrypto')
async def buy_crypto(buydata:BuyData):
    info = decode(buydata.token)
    await for_update_crypto(info['login'], buydata.type, buydata.amount)
