from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship, Mapped, mapped_column
from fastapi import HTTPException

engine = create_engine('sqlite+aiosqlite:///database.db')

session = sessionmaker(engine)

class Model(DeclarativeBase):
    pass

class User(Model):
    __tablename__ = 'user'

    id = Mapped[int] = mapped_column(primary_key=True)
    login = Mapped[str] = mapped_column(primary_key=True)
    password = Mapped[str]
    crypto = Mapped[dict] 

def for_update_crypto(login, type, amount):
    user = session.scalars(select(User).where(User.login==login))
    try:
     if type not in user.crypto:
         raise HTTPException(status_code=401, detail='Unknown type of crypto!')
     else:
         user.crypto[type]['amount'] += amount
         session.commit()
    except:
     raise HTTPException(status_code=500, detail='Something is wrong!')

users = session.query(User).all()





