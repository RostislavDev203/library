from fastapi import APIRouter, WebSocket
from pydantic import BaseModel
from database import create_new_user, authentification
import uvicorn

auth = APIRouter(prefix='/auth', tags=["Auth"])

class AuthData(BaseModel):
    login:str
    password:str

@auth.post('/sign-in')
async def sign_in(authdata:AuthData):
    create_new_user(login=authdata.login, password=authdata.password)
    

@auth.post('/log-in')
async def log_in(authdata:AuthData):
    authentification(authdata.login, authdata.password)

if __name__ == "__main__":
    uvicorn.run(port=8000)

