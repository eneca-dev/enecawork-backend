from fastapi import APIRouter, HTTPException, Request
from supabase import create_client
from app.config import settings
import json

auth_router = APIRouter()

# Инициализация клиента Supabase
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

def validate_email(email: str) -> bool:
    """Простая валидация email"""
    return '@' in email and '.' in email.split('@')[1]

def validate_registration_data(data: dict) -> None:
    """Валидация данных регистрации"""
    required_fields = [
        'first_name',
        'last_name',
        'department',
        'team',
        'position',
        'email', 
        'password'
    ]
    
    for field in required_fields:
        if not data.get(field):
            raise HTTPException(status_code=400, detail=f"Поле {field} обязательно")
    
    if not validate_email(data['email']):
        raise HTTPException(status_code=400, detail="Некорректный формат email")

@auth_router.post("/register")
async def register(request: Request):
    """
    Регистрация нового пользователя с дополнительными данными
    """
    try:
        user_data = await request.json()
        validate_registration_data(user_data)
        
        # Проверяем, существует ли пользователь
        user_response = supabase.auth.admin.list_users()
        existing_users = [user.email for user in user_response]
        
        if user_data['email'] in existing_users:
            raise HTTPException(
                status_code=400, 
                detail="Пользователь с такой почтой уже существует"
            )
        
        # Регистрируем пользователя в auth системе
        auth_response = supabase.auth.sign_up({
            "email": user_data['email'],
            "password": user_data['password']
        })
        
        # Сохраняем дополнительные данные в таблицу users
        user_data_for_table = {
            'id': auth_response.user.id,
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'department': user_data['department'],
            'team': user_data['team'],
            'position': user_data['position'],
            'email': user_data['email']
        }
        
        supabase.table('users').insert(user_data_for_table).execute()
        
        return {"message": "Регистрация успешна! Проверьте вашу почту."}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@auth_router.post("/login")
async def login(request: Request):
    """
    Вход пользователя через email и пароль
    """
    try:
        credentials = await request.json()
        
        if not credentials.get('email') or not credentials.get('password'):
            raise HTTPException(status_code=400, detail="Email и пароль обязательны")
            
        response = supabase.auth.sign_in_with_password({
            "email": credentials['email'],
            "password": credentials['password']
        })
        
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user": response.user
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Неверные учетные данные")

@auth_router.post("/reset-password")
async def reset_password(request: Request):
    """
    Отправка письма для сброса пароля
    """
    try:
        data = await request.json()
        email = data.get('email')
        
        if not email or not validate_email(email):
            raise HTTPException(status_code=400, detail="Некорректный email")
            
        response = supabase.auth.reset_password_email(email)
        return {"message": "Инструкции по восстановлению пароля отправлены"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@auth_router.post("/update-password")
async def update_password(request: Request):
    """
    Обновление пароля
    """
    try:
        data = await request.json()
        access_token = data.get('access_token')
        new_password = data.get('new_password')
        
        if not access_token or not new_password:
            raise HTTPException(
                status_code=400, 
                detail="Отсутствует токен или новый пароль"
            )
            
        response = await supabase.auth.update_user({
            "password": new_password
        })
        
        return {"message": "Пароль успешно обновлен"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@auth_router.post("/logout")
async def logout():
    """
    Выход пользователя
    """
    try:
        supabase.auth.sign_out()
        return {"message": "Успешный выход"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))