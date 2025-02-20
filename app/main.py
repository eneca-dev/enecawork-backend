from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from .config import Settings
from app.routes import auth_router

app = FastAPI(title="Auth API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутер аутентификации
app.include_router(auth_router, prefix="/auth", tags=["auth"])

# Здоровье сервера
@app.get("/")
async def health_check():
    return {"status": "healthy"} 