from gotrue.errors import AuthApiError
from app.schemas.auth import AuthRegisterResponse, AuthLoginResponse, RefreshTokenResponse
from fastapi import HTTPException, status
import logging
from supabase import Client

logger = logging.getLogger(__name__)


class AuthServices:

    @staticmethod
    def register_user(
        supabase: Client,
        first_name: str,
        last_name: str,
        department: str,
        team: str,
        position: str,
        category: str,
        email: str,
        password: str,
        password_confirm: str,
    ) -> AuthRegisterResponse:
        try:
            auth_response = supabase.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {
                        "data": {
                            "first_name": first_name,
                            "last_name": last_name,
                            "department": department,
                            "team": team,
                            "position": position,
                            "category": category,
                        }
                    },
                }
            )

            if not auth_response.user:
                logger.error("Incomplete response from Supabase")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error creating user",
                )

            user_data = {
                "id": auth_response.user.id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "department": department,
                "team": team,
                "position": position,
                "category": category,
            }

            response = supabase.from_("users").insert(user_data).execute()

            return AuthRegisterResponse(
                first_name=auth_response.user.user_metadata.get("first_name"),
                last_name=auth_response.user.user_metadata.get("last_name"),
                department=auth_response.user.user_metadata.get("department"),
                team=auth_response.user.user_metadata.get("team"),
                position=auth_response.user.user_metadata.get("position"),
                category=auth_response.user.user_metadata.get("category"),
                email=auth_response.user.email,
            )

        except AuthApiError as e:
            logger.error(f"Supabase auth error: {str(e)}")
            if "User already registered" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists",
                )
            if "rate limit" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests",
                )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @staticmethod
    def login_user(
        supabase: Client,
        email: str,
        password: str,
        device_id: str = None,
    ) -> AuthLoginResponse:
        try:
            logger.info(f"Login attempt for user: {email}, device_id: {device_id}")
            
            # Вместо использования options, мы будем использовать базовую аутентификацию
            # и затем обновлять метаданные пользователя, если это необходимо
            auth_response = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            if not auth_response.user:
                logger.warning(f"Login failed for user: {email} - No user in response")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

            # Если передан device_id, обновляем метаданные пользователя
            if device_id and auth_response.session:
                try:
                    # Обновляем метаданные пользователя
                    supabase.auth.update_user(
                        {"data": {"device_id": device_id}}
                    )
                    logger.info(f"Updated device_id for user: {email}")
                except Exception as e:
                    # Логируем ошибку, но не прерываем процесс входа
                    logger.warning(f"Failed to update user metadata: {str(e)}")

            logger.info(f"User {email} successfully logged in with device_id: {device_id}")
            return AuthLoginResponse(
                email=auth_response.user.email,
                access_token=auth_response.session.access_token,
                refresh_token=auth_response.session.refresh_token,
            )

        except AuthApiError as e:
            logger.error(f"Supabase auth error: {str(e)}")
            if "Invalid login credentials" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )
            if "Email not confirmed" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email not confirmed",
                )
            if "rate limit" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests",
                )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @staticmethod
    def reset_password(supabase: Client, email: str) -> dict:
        try:
            supabase.auth.reset_password_email(email)
            return {"message": "Email with reset link sent"}

        except AuthApiError as e:
            logger.error(f"Supabase auth error: {str(e)}")
            if "rate limit" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email"
            )

    @staticmethod
    def update_password(
        supabase: Client,
        access_token: str,
        refresh_token: str,
        password: str,
        password_confirm: str,
    ) -> dict:
        try:
            supabase.auth.set_session(access_token, refresh_token)
            supabase.auth.update_user({"password": password})
            return {"message": "Password updated successfully"}

        except AuthApiError as e:
            logger.error(f"Supabase auth error: {str(e)}")
            if "invalid token" in str(e).lower() or "invalid session" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )
            if "rate limit" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests",
                )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @staticmethod
    def refresh_token(
        supabase: Client,
        refresh_token: str,
        device_id: str = None,
    ) -> RefreshTokenResponse:
        try:
            logger.info(f"Token refresh attempt with device_id: {device_id}")
            
            # Обновляем токен без использования options
            auth_response = supabase.auth.refresh_session(refresh_token)
            
            if not auth_response.session:
                logger.warning("Token refresh failed - No session in response")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )
            
            # Если передан device_id, обновляем метаданные пользователя
            if device_id and auth_response.user:
                try:
                    # Устанавливаем сессию и обновляем метаданные
                    supabase.auth.set_session(
                        auth_response.session.access_token,
                        auth_response.session.refresh_token
                    )
                    supabase.auth.update_user(
                        {"data": {"device_id": device_id}}
                    )
                    logger.info(f"Updated device_id for user during token refresh")
                except Exception as e:
                    # Логируем ошибку, но не прерываем процесс обновления токена
                    logger.warning(f"Failed to update user metadata: {str(e)}")
            
            logger.info(f"Token successfully refreshed for device_id: {device_id}")
            return RefreshTokenResponse(
                access_token=auth_response.session.access_token,
                refresh_token=auth_response.session.refresh_token,
            )
            
        except AuthApiError as e:
            logger.error(f"Supabase auth error: {str(e)}")
            if "invalid token" in str(e).lower() or "invalid session" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Invalid refresh token"
                )
            if "rate limit" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests",
                )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
