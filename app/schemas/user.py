from pydantic import BaseModel, EmailStr, Field
from app.schemas.auth import Team, Category


class UserInformationRequest(BaseModel):
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")


class UserInformationResponse(BaseModel):
    first_name: str
    last_name: str
    department: str
    team: Team
    position: str
    category: Category
    email: EmailStr
