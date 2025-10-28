"""
Schemas para usuarios.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base schema para usuario"""
    
    email: EmailStr


class UserResponse(BaseModel):
    """Schema de respuesta de usuario"""
    
    id: UUID
    email: EmailStr
    full_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
