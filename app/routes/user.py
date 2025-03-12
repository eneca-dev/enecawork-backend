from fastapi import APIRouter, Depends, status, Request
from supabase import Client
from app.database import get_admin_client
from app.services.user import UserServices
from app.schemas.user import UserInformationRequest, UserInformationResponse

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {"example": {"detail": "Internal server error"}}
            },
        }
    },
)


@user_router.post(
    "/me",
    response_model=UserInformationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user data",
    description="Get current user data using access token",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid token",
            "content": {"application/json": {"example": {"detail": "Invalid token"}}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
            "content": {"application/json": {"example": {"detail": "User not found"}}},
        },
    },
)
def get_current_user_post(
    user_data: UserInformationRequest, supabase: Client = Depends(get_admin_client)
) -> UserInformationResponse:
    """
    Get current user data:
    - Validate access token
    - Get user ID from token
    - Return user data
    """
    return UserServices.get_current_user(supabase=supabase, **user_data.model_dump())


@user_router.get(
    "/me",
    response_model=UserInformationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user data",
    description="Get current user data using access token from Authorization header",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid token",
            "content": {"application/json": {"example": {"detail": "Invalid token"}}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
            "content": {"application/json": {"example": {"detail": "User not found"}}},
        },
    },
)
def get_current_user(
    request: Request, supabase: Client = Depends(get_admin_client)
) -> UserInformationResponse:
    """
    Get current user data:
    - Extract token from Authorization header
    - Validate access token
    - Get user ID from token
    - Return user data
    """
    return UserServices.get_current_user_from_header(supabase=supabase, request=request)
