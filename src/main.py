from .router import auth, home, buycrypto
from fastapi import FastAPI

app = FastAPI()
app.include_router(auth)
app.include_router(home)
app.include_router(buycrypto)

