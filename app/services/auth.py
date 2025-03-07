from gotrue.errors import AuthApiError
from app.schemas.auth import AuthRegisterResponse, AuthLoginResponse
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
    ) -> AuthLoginResponse:
        try:
            auth_response = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            if not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

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
