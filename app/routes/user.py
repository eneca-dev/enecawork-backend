from fastapi import APIRouter, Depends, status, Header, HTTPException
from supabase import Client
from app.database import get_admin_client
from app.services.user import UserServices
from app.schemas.user import UserInformationResponse
from typing import Optional

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "Internal server error"}
                }
            },
        }
    },
)


async def get_token_from_header(
    authorization: Optional[str] = Header(None)
) -> str:
    """
    Extract token from Authorization header
    """
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use 'Bearer <token>'",
        )
    
    return parts[1]


@user_router.get(
    "/me",
    response_model=UserInformationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user data",
    description="Get current user data using access token from Authorization header",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid token or missing Authorization header",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_token": {
                            "value": {"detail": "Invalid token"}
                        },
                        "missing_header": {
                            "value": {"detail": "Authorization header is missing"}
                        },
                        "invalid_format": {
                            "value": {
                                "detail": "Invalid authorization header format. Use 'Bearer <token>'"
                            }
                        }
                    }
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            },
        },
    },
)
async def get_current_user(
    token: str = Depends(get_token_from_header),
    supabase: Client = Depends(get_admin_client)
) -> UserInformationResponse:
    """
    Get current user data:
    - Extract access token from Authorization header
    - Validate access token
    - Get user ID from token
    - Return user data
    """
    return UserServices.get_current_user(supabase=supabase, access_token=token)
