from fastapi import APIRouter, HTTPException, Request
from supabase import create_client
from app.config import settings
import json

auth_router = APIRouter()

# Инициализация клиента Supabase
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

def validate_email(email: str) -> bool:
    """
    Проверяет корректность формата email адреса.
    
    Args:
        email (str): Email адрес для проверки
    
    Returns:
        bool: True если email корректен, False в противном случае
    
    Пример:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid.email")
        False
    """
    return '@' in email and '.' in email.split('@')[1]

def validate_registration_data(data: dict) -> None:
    """
    Проверяет наличие всех необходимых полей в данных регистрации.
    
    Args:
        data (dict): Словарь с данными пользователя
    
    Raises:
        HTTPException: Если отсутствует обязательное поле или некорректный email
    
    Проверяемые поля:
        - first_name: Имя пользователя
        - last_name: Фамилия пользователя
        - department: Отдел
        - team: Команда
        - position: Должность
        - email: Email адрес
        - password: Пароль
    """
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
    Регистрирует нового пользователя в системе.
    
    Args:
        request (Request): FastAPI запрос, содержащий JSON с данными пользователя
    
    Returns:
        dict: Сообщение об успешной регистрации
    
    Raises:
        HTTPException: 
            - 400: Если пользователь уже существует
            - 400: При ошибке валидации данных
            - 400: При ошибке создания пользователя
    
    Процесс:
        1. Валидация входных данных
        2. Проверка существования пользователя
        3. Создание пользователя в auth системе
        4. Сохранение дополнительных данных в таблице users
    """
    try:
        user_data = await request.json()
        validate_registration_data(user_data)
        
        user_response = supabase.auth.admin.list_users()
        existing_users = [user.email for user in user_response]
        
        if user_data['email'] in existing_users:
            raise HTTPException(
                status_code=400, 
                detail="Пользователь с такой почтой уже существует"
            )
        
        auth_response = supabase.auth.sign_up({
            "email": user_data['email'],
            "password": user_data['password']
        })
        
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
    Аутентифицирует пользователя в системе.
    
    Args:
        request (Request): FastAPI запрос с email и паролем
    
    Returns:
        dict: Токены доступа и данные пользователя
            - access_token: JWT токен для доступа
            - refresh_token: Токен для обновления access_token
            - user: Информация о пользователе
    
    Raises:
        HTTPException:
            - 400: Если отсутствует email или пароль
            - 401: При неверных учетных данных
    
    Примечание:
        Токены следует хранить в безопасном месте на клиенте
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
    Отправляет письмо для сброса пароля на указанный email.
    
    Args:
        request (Request): FastAPI запрос с email адресом
    
    Returns:
        dict: Сообщение об отправке инструкций
    
    Raises:
        HTTPException:
            - 400: При некорректном email
            - 400: При ошибке отправки письма
    
    Примечание:
        Письмо содержит ссылку для сброса пароля с ограниченным временем действия
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
    Обновляет пароль пользователя.
    
    Args:
        request (Request): FastAPI запрос, содержащий:
            - access_token: Токен доступа
            - refresh_token: Токен обновления
            - new_password: Новый пароль
    
    Returns:
        dict: Сообщение об успешном обновлении пароля
    
    Raises:
        HTTPException:
            - 400: При отсутствии токенов или пароля
            - 400: При ошибке обновления пароля
    """
    try:
        data = await request.json()
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        new_password = data.get('new_password')
        
        if not access_token or not refresh_token or not new_password:
            raise HTTPException(
                status_code=400, 
                detail="Отсутствует токен доступа, токен обновления или новый пароль"
            )

        try:
            session = supabase.auth.set_session(access_token, refresh_token)
        except Exception as session_error:
            raise HTTPException(status_code=400, detail=f"Ошибка установки сессии: {str(session_error)}")
        
        try:
            response = supabase.auth.update_user({
                "password": new_password
            })
        except Exception as update_error:
            raise HTTPException(status_code=400, detail=f"Ошибка обновления пароля: {str(update_error)}")
        
        return {"message": "Пароль успешно обновлен"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@auth_router.post("/logout")
async def logout():
    """
    Выход пользователя из системы.
    
    Returns:
        dict: Сообщение об успешном выходе
    
    Raises:
        HTTPException: 400 при ошибке выхода
    
    Действия:
        1. Инвалидация текущей сессии в Supabase
        2. Очистка токенов на стороне сервера
    
    Примечание:
        Клиент должен также удалить сохраненные токены
    """
    try:
        supabase.auth.sign_out()
        return {"message": "Успешный выход"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))