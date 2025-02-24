from fastapi import APIRouter, HTTPException, Request
from supabase import create_client
from app.config import settings

users_router = APIRouter()

# Инициализация клиента Supabase
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

@users_router.get("/profile")
async def get_user_profile(request: Request):
    """
    Получает профиль пользователя из базы данных.
    
    Args:
        request (Request): FastAPI запрос с заголовком Authorization
    
    Returns:
        dict: Данные пользователя
            - first_name: Имя
            - last_name: Фамилия
            - department: Отдел
            - team: Команда
            - position: Должность
            - email: Email адрес
    
    Raises:
        HTTPException:
            - 401: Если токен отсутствует или недействителен
            - 404: Если пользователь не найден
            - 400: При ошибке получения данных
    """
    try:
        # Получаем токен из заголовка
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(
                status_code=401, 
                detail="Отсутствует токен авторизации"
            )
        
        # Извлекаем токен
        token = auth_header.split(' ')[1]
        
        # Получаем данные пользователя из токена
        user = supabase.auth.get_user(token)
        if not user:
            raise HTTPException(
                status_code=401, 
                detail="Недействительный токен"
            )
        
        # Получаем расширенные данные из таблицы users
        response = supabase.table('users').select('*').eq('id', user.user.id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=404,
                detail="Профиль пользователя не найден"
            )
            
        return response.data[0]
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 