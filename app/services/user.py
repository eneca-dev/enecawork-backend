import logging
from supabase import Client
from fastapi import HTTPException, status, Request
from app.schemas.user import UserInformationResponse

logger = logging.getLogger(__name__)


class UserServices:
    @staticmethod
    def get_current_user_from_header(
        supabase: Client, request: Request
    ) -> UserInformationResponse:
        # Получаем заголовок Authorization
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid authorization header"
            )
        
        # Извлекаем токен
        access_token = auth_header.replace("Bearer ", "")
        
        try:
            # Вместо установки сессии с None в качестве refresh_token,
            # используем заголовок Authorization напрямую
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Получаем текущего пользователя с использованием заголовка
            user_response = supabase.auth.get_user(jwt=access_token)
            user_id = user_response.user.id
            
            if not user_response:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )
            
            # Получаем дополнительные данные пользователя из таблицы users
            query = supabase.from_("users").select("*").filter("id", "eq", user_id)
            response = query.execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            
            user_data = response.data[0]
            # Добавляем email из данных аутентификации, если его нет в таблице users
            if 'email' not in user_data and hasattr(user_response.user, 'email'):
                user_data['email'] = user_response.user.email
            
            return UserInformationResponse(**user_data)
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication error: {str(e)}",
            )
