"""
Esquemas de autenticación.
"""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Esquema para solicitud de login"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Esquema para respuesta de token"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """Esquema para respuesta de usuario"""
    id: str
    email: str
    full_name: str | None
    is_active: bool