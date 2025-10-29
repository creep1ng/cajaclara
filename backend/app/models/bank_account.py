"""
Modelo de cuenta bancaria para gestión de cuentas del usuario.
"""

from sqlalchemy import Column, Numeric, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class BankAccount(Base, UUIDMixin, TimestampMixin):
    """Modelo de cuenta bancaria"""
    
    __tablename__ = "bank_accounts"
    __table_args__ = (
        {"comment": "Cuentas bancarias de los usuarios"},
    )
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID del usuario propietario de la cuenta"
    )
    
    name = Column(
        String(100),
        nullable=False,
        comment="Nombre de la cuenta bancaria"
    )
    
    color = Column(
        String(7),
        nullable=False,
        default="#3B82F6",
        comment="Color en formato hexadecimal (#RRGGBB)"
    )
    
    initial_balance = Column(
        Numeric(12, 2),
        nullable=False,
        comment="Saldo inicial de la cuenta"
    )
    
    current_balance = Column(
        Numeric(12, 2),
        nullable=False,
        comment="Saldo actual de la cuenta"
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="bank_accounts"
    )
    
    def __repr__(self) -> str:
        return f"<BankAccount(id={self.id}, name={self.name}, user_id={self.user_id})>"
