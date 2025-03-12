from pydantic import BaseModel, EmailStr, Field
from app.schemas.auth import Team, Category


class UserInformationRequest(BaseModel):
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")


class UserInformationResponse(BaseModel):
    id: str
    email: EmailStr
    department_id: str = None
    team_id: str = None
    position_id: str = None
    category_id: str = None
    created_at: str = None
    first_name: str = None
    last_name: str = None
