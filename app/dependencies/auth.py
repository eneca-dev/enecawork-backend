from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client
from uuid import UUID
import logging
from app.database import get_supabase

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase),
) -> UUID:
    """
    Получает ID текущего пользователя из токена авторизации
    """
    try:
        # Получаем access_token из заголовка
        access_token = credentials.credentials

        # Получаем данные пользователя без установки сессии
        response = supabase.auth.get_user(access_token)

        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен авторизации",
            )

        return UUID(response.user.id)

    except Exception as e:
        logger.error(f"Ошибка аутентификации: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Ошибка аутентификации"
        )
