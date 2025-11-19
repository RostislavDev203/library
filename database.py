from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine
from fastapi import HTTPException
import random
import bcrypt
from auth import sign

salt = bcrypt.gensalt()

engine = create_async_engine('sqlite:///database.db')

session = sessionmaker(engine)

class Model(DeclarativeBase):
    pass

class User(Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, nullable=False)
    login = Column(String, primary_key=True, nullable=False)
    password = Column(String, nullable=False)

users = session.query(User).all()

def create_new_user(login:str, password:str):
    for user in users:
        if user.login == login:
            raise HTTPException(status_code=401, detail='This login is already taken!')
        else:
            continue
    try:
        session.add(User(id=random.randint(1, 9999999999), login=login, password=bcrypt.hashpw(password, salt=salt)))
        session.commit()
        return {'details': 'Successful creating!'}
    except:
        raise HTTPException(status_code=500, detail='Something is wrong, try later!')
    

def authentification(login:str, password:str):
    for user in users:
        if user.login == login and bcrypt.checkpw(user.password, salt) == password:
            new_sign = sign(login=login)
            return new_sign
        else:
            raise HTTPException(status_code=401, detail='Invalid login or password!')



