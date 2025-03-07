import logging
from supabase import Client
from fastapi import HTTPException, status
from app.schemas.user import UserInformationResponse

logger = logging.getLogger(__name__)


class UserServices:
    @staticmethod
    def get_current_user(
        supabase: Client, access_token: str, refresh_token: str
    ) -> UserInformationResponse:

        # Set session with tokens
        supabase.auth.set_session(access_token, refresh_token)

        # Get current user
        user_response = supabase.auth.get_user()
        user_id = user_response.user.id

        if not user_response:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        # Get additional user data from users table
        try:
            query = supabase.from_("users").select("*").filter("id", "eq", user_id)
            response = query.execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            user_data = response.data[0]
            return UserInformationResponse(**user_data)

        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )
