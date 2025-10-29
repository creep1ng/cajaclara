"""
Schemas para categorías y reglas de categorización.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """Base schema para categoría"""

    id: str = Field(max_length=50, description="ID de categoría")
    name: str = Field(max_length=100, description="Nombre")
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    transaction_type: str = Field(pattern="^(income|expense)$")
    description: Optional[str] = None
    predefined: bool = True


class CategoryResponse(CategoryBase):
    """Schema de respuesta de categoría"""

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CategoryListResponse(BaseModel):
    """Lista de categorías"""

    categories: List[CategoryResponse]


class MatchingCriteria(BaseModel):
    """Criterios de coincidencia para reglas"""

    keywords: Optional[List[str]] = Field(
        None, description="Palabras clave a buscar (OR)"
    )
    min_amount: Optional[Decimal] = Field(None, ge=0)
    max_amount: Optional[Decimal] = Field(None, ge=0)
    vendor_patterns: Optional[List[str]] = Field(
        None, description="Patrones de nombres de vendedor"
    )


class CreateCategoryRuleRequest(BaseModel):
    """Schema para crear regla de categorización"""

    rule_name: str = Field(max_length=100)
    category_id: str = Field(max_length=50)
    matching_criteria: MatchingCriteria
    enabled: bool = True


class CategoryRuleResponse(BaseModel):
    """Schema de respuesta de regla"""

    id: str
    user_id: str
    rule_name: str
    category_id: str
    matching_criteria: dict
    enabled: bool
    times_applied: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
