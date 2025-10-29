"""
Exportación de todos los schemas Pydantic.
"""

from app.schemas.category import (
    CategoryListResponse,
    CategoryResponse,
    CategoryRuleResponse,
    CreateCategoryRuleRequest,
    MatchingCriteria,
)
from app.schemas.common import (
    ErrorDetail,
    ErrorResponse,
    PaginationInfo,
    PaginationParams,
    SuccessResponse,
)
from app.schemas.transaction import (
    ClassificationSummary,
    CreateManualTransactionRequest,
    TransactionFilters,
    TransactionListResponse,
    TransactionMetadata,
    TransactionResponse,
    TransactionSummary,
    UpdateTransactionRequest,
)
from app.schemas.user import UserResponse

__all__ = [
    # Common
    "PaginationParams",
    "PaginationInfo",
    "ErrorDetail",
    "ErrorResponse",
    "SuccessResponse",
    # Category
    "CategoryResponse",
    "CategoryListResponse",
    "MatchingCriteria",
    "CreateCategoryRuleRequest",
    "CategoryRuleResponse",
    # Transaction
    "CreateManualTransactionRequest",
    "UpdateTransactionRequest",
    "TransactionMetadata",
    "TransactionResponse",
    "TransactionFilters",
    "ClassificationSummary",
    "TransactionSummary",
    "TransactionListResponse",
    # User
    "UserResponse",
]
