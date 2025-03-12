from pydantic import BaseModel, EmailStr, model_validator, Field
from enum import Enum


class Team(str, Enum):
    GENERAL = "general"
    # add other teams


class Category(str, Enum):
    GENERAL = "general"
    # add other categories


class PasswordValidatorMixin:
    """Mixin for password validation"""

    @property
    def password_strength(self) -> str:
        password = self.password
        if len(password) < 6:
            raise ValueError("Password must contain at least 6 characters")
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isalpha() for char in password):
            raise ValueError("Password must contain at least one letter")
        return password


class AuthRegisterRequest(BaseModel, PasswordValidatorMixin):
    first_name: str = Field(..., min_length=2, description="Name of the user")
    last_name: str = Field(..., min_length=2, description="Surname of the user")
    department: str = Field(..., description="Department")
    team: Team = Field(default=Team.GENERAL, description="Team")
    position: str = Field(..., description="Position")
    category: Category = Field(default=Category.GENERAL, description="Category")
    email: EmailStr = Field(..., description="Email of the user")
    password: str = Field(..., description="Password")
    password_confirm: str = Field(..., description="Password confirmation")

    @model_validator(mode="after")
    def validate_passwords(self) -> "AuthRegisterRequest":
        self.password_strength
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class AuthRegisterResponse(BaseModel):
    first_name: str
    last_name: str
    department: str
    team: Team
    position: str
    category: Category
    email: EmailStr


class AuthLoginRequest(BaseModel, PasswordValidatorMixin):
    email: EmailStr = Field(..., description="Email of the user")
    password: str = Field(..., description="Password")

    @model_validator(mode="after")
    def validate_password(self) -> "AuthLoginRequest":
        self.password_strength
        return self


class AuthLoginResponse(BaseModel):
    email: EmailStr
    access_token: str
    refresh_token: str


class AuthResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Email for password reset")


class AuthUpdatePasswordRequest(BaseModel, PasswordValidatorMixin):
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
    password: str = Field(..., description="New password")
    password_confirm: str = Field(..., description="New password confirmation")

    @model_validator(mode="after")
    def validate_passwords(self) -> "AuthUpdatePasswordRequest":
        self.password_strength
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
