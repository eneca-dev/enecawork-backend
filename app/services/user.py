import logging
from supabase import Client
from fastapi import HTTPException, status
from app.schemas.user import UserInformationResponse
from gotrue.errors import AuthApiError

logger = logging.getLogger(__name__)


class UserServices:
    @staticmethod
    def get_current_user(
        supabase: Client,
        access_token: str,
    ) -> UserInformationResponse:
        """
        Get current user data using access token
        """
        try:
            # Set session with the provided access token
            supabase.auth.set_session(access_token, None)
            
            # Get user from session
            user = supabase.auth.get_user()
            
            if not user or not user.user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            
            # Get user data from database
            user_id = user.user.id
            response = supabase.from_("users").select("*").eq("id", user_id).execute()
            
            if not response.data or len(response.data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found in database",
                )
            
            user_data = response.data[0]
            
            return UserInformationResponse(
                id=user_data.get("id"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                email=user.user.email,
                department=user_data.get("department"),
                team=user_data.get("team"),
                position=user_data.get("position"),
                category=user_data.get("category"),
            )
            
        except AuthApiError as e:
            logger.error(f"Supabase auth error: {str(e)}")
            if "invalid token" in str(e).lower() or "invalid session" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
