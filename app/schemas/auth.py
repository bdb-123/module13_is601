# app/schemas/auth.py

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, ConfigDict

class UserRegister(BaseModel):
    """
    Schema for user registration.
    Validates email format, password strength, and optional password confirmation.
    """
    email: EmailStr = Field(
        description="User's email address",
        examples=["john.doe@example.com"]
    )
    username: str = Field(
        min_length=3,
        max_length=50,
        description="Username (3-50 characters)",
        examples=["johndoe"]
    )
    first_name: str = Field(
        min_length=1,
        max_length=50,
        description="User's first name",
        examples=["John"]
    )
    last_name: str = Field(
        min_length=1,
        max_length=50,
        description="User's last name",
        examples=["Doe"]
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Password (minimum 8 characters)",
        examples=["SecurePass123!"]
    )
    confirm_password: Optional[str] = Field(
        default=None,
        min_length=8,
        max_length=128,
        description="Password confirmation (optional, but must match if provided)",
        examples=["SecurePass123!"]
    )

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password meets strength requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        
        return v

    @model_validator(mode='after')
    def verify_password_match(self) -> 'UserRegister':
        """Verify that password and confirm_password match if confirm_password is provided."""
        if self.confirm_password is not None and self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john.doe@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!"
            }
        }
    )


class UserLogin(BaseModel):
    """
    Schema for user login.
    Accepts email and password for authentication.
    """
    email: str = Field(
        description="User's email address or username",
        examples=["john.doe@example.com", "johndoe"]
    )
    password: str = Field(
        min_length=1,  # Don't validate length on login (only on registration)
        description="User's password",
        examples=["SecurePass123!"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john.doe@example.com",
                "password": "SecurePass123!"
            }
        }
    )


class TokenResponse(BaseModel):
    """
    Schema for authentication token response.
    Returns JWT access token with bearer type.
    """
    access_token: str = Field(
        description="JWT access token",
        examples=["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"]
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')",
        examples=["bearer"]
    )
    refresh_token: Optional[str] = Field(
        default=None,
        description="JWT refresh token (optional)",
        examples=["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        }
    )


class ErrorResponse(BaseModel):
    """
    Schema for error responses.
    Provides consistent error messaging.
    """
    detail: str = Field(
        description="Error message",
        examples=["Invalid credentials"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Invalid email or password"
            }
        }
    )
