# app/schemas/__init__.py
from .user import (
    UserBase,
    UserCreate,
    UserResponse,
    UserLogin,
    UserUpdate,
    PasswordUpdate
)

from .token import Token, TokenData, TokenResponse

from .auth import (
    UserRegister,
    UserLogin as AuthUserLogin,
    TokenResponse as AuthTokenResponse,
    ErrorResponse
)

from .calculation import (
    CalculationType,
    CalculationBase,
    CalculationCreate,
    CalculationUpdate,
    CalculationResponse
)

__all__ = [
    'UserBase',
    'UserCreate',
    'UserResponse',
    'UserLogin',
    'UserUpdate',
    'PasswordUpdate',
    'Token',
    'TokenData',
    'TokenResponse',
    # Auth schemas
    'UserRegister',
    'AuthUserLogin',
    'AuthTokenResponse',
    'ErrorResponse',
    # Calculation schemas
    'CalculationType',
    'CalculationBase',
    'CalculationCreate',
    'CalculationUpdate',
    'CalculationResponse',
]