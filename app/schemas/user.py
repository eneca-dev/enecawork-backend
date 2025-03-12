from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from app.schemas.auth import Team, Category


class UserInformationResponse(BaseModel):
    """Schema for user information response"""
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    department: str
    team: Team
    position: str
    category: Category
