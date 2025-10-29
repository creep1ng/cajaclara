"""
Modelo de transacciones financieras.
"""

from typing import Any, Optional

from app.models.base import (AuditMixin, Base, SoftDeleteMixin, TimestampMixin,
                             UUIDMixin)
from sqlalchemy import (ARRAY, Column, DateTime, ForeignKey, Index, Numeric,
                        String, Text)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship


class Transaction(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Modelo de transacción financiera"""
    
    __tablename__ = "transactions"
    __table_args__ = (
        Index("idx_transactions_user", "user_id"),
        Index("idx_transactions_entrepreneurship", "entrepreneurship_id"),
        Index("idx_transactions_date", "transaction_date"),
        Index("idx_transactions_type", "transaction_type"),
        Index("idx_transactions_classification", "classification"),
        Index("idx_transactions_category", "category_id"),
        Index("idx_transactions_deleted", "deleted_at", postgresql_where=Column("deleted_at").is_(None)),
        Index("idx_transactions_metadata", "metadata", postgresql_using="gin"),
        {"comment": "Transacciones financieras (ingresos y gastos)"},
    )
    
    # Foreign Keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="Usuario propietario"
    )
    
    entrepreneurship_id = Column(
        UUID(as_uuid=True),
        ForeignKey("entrepreneurships.id", ondelete="SET NULL"),
        nullable=True,
        comment="Emprendimiento asociado (opcional)"
    )
    
    category_id = Column(
        String(50),
        ForeignKey("categories.id"),
        nullable=True,
        comment="Categoría de la transacción"
    )
    
    # Transaction Data
    amount = Column(
        Numeric(15, 2),
        nullable=False,
        comment="Monto de la transacción"
    )
    
    currency = Column(
        String(3),
        default="COP",
        nullable=False,
        comment="Moneda (ISO 4217)"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Descripción o nota"
    )
    
    transaction_type = Column(
        String(20),
        nullable=False,
        comment="Tipo: income, expense o transfer"
    )
    
    classification = Column(
        String(20),
        nullable=False,
        comment="Clasificación: personal o business"
    )
    
    transaction_date = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha y hora de la transacción"
    )
    
    # Sync Status (para offline-first)
    sync_status = Column(
        String(20),
        default="synced",
        nullable=False,
        comment="Estado de sincronización: pending, synced, failed"
    )
    
    # Transfer Data (para transferencias entre cuentas)
    from_account = Column(
        String(50),
        nullable=True,
        comment="Cuenta de origen (para transferencias)"
    )
    
    to_account = Column(
        String(50),
        nullable=True,
        comment="Cuenta de destino (para transferencias)"
    )
    
    # Additional Data
    tags = Column(
        ARRAY(Text),
        nullable=True,
        comment="Etiquetas adicionales"
    )
    
    extra_data = Column(
        "metadata",  # Nombre en DB
        JSONB,
        nullable=True,
        comment="Metadatos adicionales (source, ocr_confidence, etc.)"
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="transactions",
        foreign_keys=[user_id]
    )
    
    entrepreneurship = relationship(
        "Entrepreneurship",
        back_populates="transactions"
    )
    
    category = relationship(
        "Category",
        back_populates="transactions"
    )
    
    def __repr__(self) -> str:
        return (
            f"<Transaction(id={self.id}, amount={self.amount}, "
            f"type={self.transaction_type}, date={self.transaction_date})>"
        )
    
    @property
    def is_income(self) -> bool:
        """Check if transaction is income"""
        return self.transaction_type == "income"
    
    @property
    def is_expense(self) -> bool:
        """Check if transaction is expense"""
        return self.transaction_type == "expense"
    
    @property
    def is_business(self) -> bool:
        """Check if transaction is business"""
        return self.classification == "business"
    
    @property
    def is_personal(self) -> bool:
        """Check if transaction is personal"""
        return self.classification == "personal"
    
    def get_metadata_value(self, key: str, default: Optional[Any] = None) -> Any:
        """Get value from extra_data JSONB"""
        if self.extra_data is None:
            return default
        return self.extra_data.get(key, default)
