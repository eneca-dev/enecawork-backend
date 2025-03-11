from supabase import Client
from app.services.auth import AuthServices
from app.database import get_supabase, get_admin_client
from fastapi import APIRouter, Depends, status
from app.schemas.auth import (
    AuthRegisterRequest,
    AuthRegisterResponse,
    AuthLoginRequest,
    AuthLoginResponse,
    AuthResetPasswordRequest,
    AuthUpdatePasswordRequest,
    AuthRefreshTokenRequest,
    AuthRefreshTokenResponse,
)


auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {"example": {"detail": "Internal server error"}}
            },
        }
    },
)


@auth_router.post(
    "/register",
    response_model=AuthRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create new user with specified data and send email for confirmation",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid data",
            "content": {
                "application/json": {
                    "examples": {
                        "password_mismatch": {
                            "value": {"detail": "Passwords do not match"}
                        },
                        "email_exists": {
                            "value": {"detail": "User with this email already exists"}
                        },
                    }
                }
            },
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Too many requests"},
    },
)
def register(
    user_data: AuthRegisterRequest, supabase: Client = Depends(get_admin_client)
) -> AuthRegisterResponse:
    """
    Register new user:
    - Check validity of data
    - Create new user
    - Send email for confirmation
    """
    result = AuthServices.register_user(supabase=supabase, **user_data.model_dump())
    return result


@auth_router.post(
    "/login",
    response_model=AuthLoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login to system",
    description="Authenticate user and return access tokens",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {"example": {"detail": "Invalid email or password"}}
            },
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Too many requests"},
    },
)
def login(
    user_data: AuthLoginRequest, supabase: Client = Depends(get_supabase)
) -> AuthLoginResponse:
    """
    Login to system:
    - Check credentials
    - Return access tokens on successful authentication
    """
    result = AuthServices.login_user(supabase=supabase, **user_data.model_dump())
    return result


@auth_router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Send email with link to reset password",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid email"},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Too many requests"},
    },
)
def reset_password(
    user_data: AuthResetPasswordRequest, supabase: Client = Depends(get_supabase)
) -> dict:
    """
    Request password reset:
    - Check if email exists
    - Send email with link to reset password
    """
    result = AuthServices.reset_password(supabase=supabase, **user_data.model_dump())
    return {"message": "Email with reset link sent"}


@auth_router.post(
    "/update-password",
    status_code=status.HTTP_200_OK,
    summary="Update password",
    description="Update user password",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid data",
            "content": {
                "application/json": {
                    "examples": {
                        "password_mismatch": {
                            "value": {"detail": "Passwords do not match"}
                        },
                        "weak_password": {"value": {"detail": "Password is too weak"}},
                    }
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid token"},
    },
)
def update_password(
    user_data: AuthUpdatePasswordRequest, supabase: Client = Depends(get_supabase)
) -> dict:
    """
    Update password:
    - Check validity of tokens
    - Check new password
    - Update user password
    """
    result = AuthServices.update_password(supabase=supabase, **user_data.model_dump())
    return {"message": "Password updated successfully"}


@auth_router.post(
    "/refresh-token",
    response_model=AuthRefreshTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Update access token",
    description="Update access token using refresh token",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid refresh token",
            "content": {
                "application/json": {"example": {"detail": "Invalid refresh token"}}
            },
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Too many requests"},
    },
)
def refresh_token(
    token_data: AuthRefreshTokenRequest, supabase: Client = Depends(get_supabase)
) -> AuthRefreshTokenResponse:
    """
    Update tokens:
    - Check validity of refresh token
    - Generate new pair of tokens
    """
    result = AuthServices.refresh_token(supabase=supabase, **token_data.model_dump())
    return result
