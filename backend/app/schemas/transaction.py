from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator


class TransactionCreate(BaseModel):
    client_id: Optional[str] = Field(None, description="UUID generado por el cliente para deduplicación offline")
    transaction_type: str = Field(..., description="Tipo de transacción: income o expense")
    amount: Decimal = Field(..., gt=0, description="Monto de la transacción, debe ser > 0")
    currency: Optional[str] = Field("COP", max_length=3)
    category_id: str
    account_id: str
    description: Optional[str] = Field(None, max_length=500)
    recipient: Optional[str] = Field(None, max_length=200)
    classification: Optional[str] = Field(None)
    transaction_date: datetime
    metadata: Optional[dict] = None

    @validator("transaction_type")
    def check_type(cls, v: str) -> str:
        v = v.lower()
        if v not in ("income", "expense"):
            raise ValueError("transaction_type must be 'income' or 'expense'")
        return v

    class Config:
        orm_mode = True


class TransactionRead(BaseModel):
    id: str
    client_id: Optional[str]
    user_id: str
    transaction_type: str
    amount: Decimal
    currency: str
    category_id: str
    account_id: str
    description: Optional[str]
    recipient: Optional[str]
    classification: Optional[str]
    transaction_date: datetime
    sync_status: Optional[str]
    metadata: Optional[dict]
    deleted: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
# Pydantic schema Transaction
# ...existing code...
