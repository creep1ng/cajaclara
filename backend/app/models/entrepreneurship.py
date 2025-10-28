"""
Modelo de emprendimientos para asociar transacciones con negocios específicos.
"""

from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Entrepreneurship(Base, UUIDMixin, TimestampMixin):
    """Modelo de emprendimiento o negocio del usuario"""
    
    __tablename__ = "entrepreneurships"
    __table_args__ = (
        {"comment": "Emprendimientos o negocios de los usuarios"},
    )
    
    # Foreign Keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Usuario propietario"
    )
    
    # Business Data
    name = Column(
        String(255),
        nullable=False,
        comment="Nombre del emprendimiento"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Descripción del emprendimiento"
    )
    
    business_type = Column(
        String(100),
        nullable=True,
        comment="Tipo de negocio (ej: retail, services, manufacturing)"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Si el emprendimiento está activo"
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="entrepreneurships"
    )
    
    transactions = relationship(
        "Transaction",
        back_populates="entrepreneurship"
    )
    
    def __repr__(self) -> str:
        return f"<Entrepreneurship(id={self.id}, name={self.name}, user_id={self.user_id})>"