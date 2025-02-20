from fastapi import APIRouter, HTTPException, Request, Form
from supabase import create_client
from pydantic import BaseModel, EmailStr
from ..config import settings

# Определение модели для учетных данных пользователя
class UserCredentials(BaseModel):
    email: str
    password: str

auth_router = APIRouter()

# Инициализация клиента Supabase
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

class UserRegistration(BaseModel):
    first_name: str
    last_name: str
    department: str
    team: str
    position: str
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordUpdate(BaseModel):
    token: str
    new_password: str

class UpdatePasswordRequest(BaseModel):
    access_token: str
    new_password: str

@auth_router.post("/register")
async def register(user_data: UserRegistration):
    """
    Регистрация нового пользователя с дополнительными данными
    """
    try:
        # Проверяем, существует ли пользователь
        user_response = supabase.auth.admin.list_users()
        existing_users = [user.email for user in user_response]
        
        if user_data.email in existing_users:
            raise HTTPException(
                status_code=400, 
                detail="Пользователь с такой почтой уже существует"
            )
        
        # Регистрируем пользователя в auth системе
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password
        })
        
        # Сохраняем дополнительные данные в таблицу users
        user_data_dict = user_data.dict(exclude={'password'})
        user_data_dict['id'] = auth_response.user.id
        
        supabase.table('users').insert(user_data_dict).execute()
        
        return {"message": "Регистрация успешна! Проверьте вашу почту."}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@auth_router.post("/login")
async def login(credentials: UserCredentials):
    """
    Вход пользователя через email и пароль
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user": response.user
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Неверные учетные данные")


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

@auth_router.post("/reset-password")
async def reset_password(request: PasswordResetRequest):
    """
    Отправка письма для сброса пароля
    """
    try:
        response = supabase.auth.reset_password_email(request.email)
        return {"message": "Инструкции по восстановлению пароля отправлены"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@auth_router.get("/update-password")
async def update_password_page(request: Request):
    return templates.TemplateResponse(
        "update_password.html",  # Создайте соответствующий шаблон
        {"request": request}
    )

@auth_router.post("/update-password")
async def update_password(
    request: UpdatePasswordRequest
):
    try:
        # Обновляем пароль через Supabase
        response = await supabase.auth.update_user({
            "password": request.new_password
        })
        
        return {"message": "Пароль успешно обновлен"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))