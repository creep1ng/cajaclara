"""
Schemas para gestión de cuentas bancarias.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BankAccountBase(BaseModel):
    """Campos compartidos entre operaciones de cuentas."""

    name: str = Field(min_length=1, max_length=100)
    color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    initial_balance: Decimal = Field(ge=0, decimal_places=2)


class CreateBankAccountRequest(BankAccountBase):
    """Datos requeridos para crear una cuenta."""

    current_balance: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)


class UpdateBankAccountRequest(BaseModel):
    """Campos opcionales para actualizar una cuenta."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    color: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    initial_balance: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)
    current_balance: Optional[Decimal] = Field(default=None, ge=0, decimal_places=2)


class BankAccountResponse(BaseModel):
    """Respuesta serializada de una cuenta bancaria."""

    id: UUID
    user_id: UUID
    name: str
    color: str
    initial_balance: Decimal
    current_balance: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BankAccountListResponse(BaseModel):
    """Respuesta para listados de cuentas."""

    accounts: List[BankAccountResponse]
    total: int
