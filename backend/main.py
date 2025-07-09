from fastapi import FastAPI
from backend.telegram_webhook import router as telegram_router

app = FastAPI()
app.include_router(telegram_router) 