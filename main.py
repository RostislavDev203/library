#new code
import random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    username:str
    password:str

class Guess(BaseModel):
    number:int

class Bank_Account(BaseModel):
    id:int

class Bank_Post(Bank_Account):
    new_sum:int

balance = []
users = {"user2": "321"}

@app.post("/login")
async def login(user: User):
    if user.password != users.get("user1"):
        raise HTTPException(status_code=401, detail="Неверный пароль!")
    else:
        return {"message": "Добро пожаловать!"}

@app.post("/guess_number")
async def guess_number(guess: Guess):
    random_number = random.randint(0, 10)
    if guess.number != random_number:
        return {"message": "Число неверно!"}
    else:
        return {"users": "Число верно!"}
    
@app.post("/get")
async def get_info(account: Bank_Account):
    try:
        return {"balance": balance[account.id]}
    except:
        raise HTTPException(status_code=401, detail="Баланс не найден!")
    
@app.post("/put")
async def put_info(account: Bank_Post):
    balance.insert(account.id, account.new_sum)

@app.post("/delete")
async def delete_info(account: Bank_Account):
    balance.pop(account.id)
