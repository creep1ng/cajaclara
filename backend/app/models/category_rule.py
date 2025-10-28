"""
Modelo de reglas de categorización automática.
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class CategoryRule(Base, UUIDMixin, TimestampMixin):
    """Modelo de regla de categorización automática"""
    
    __tablename__ = "category_rules"
    __table_args__ = (
        {"comment": "Reglas para categorización automática de transacciones"},
    )
    
    # Foreign Keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Usuario propietario"
    )
    
    category_id = Column(
        String(50),
        ForeignKey("categories.id"),
        nullable=False,
        comment="Categoría a aplicar"
    )
    
    # Rule Data
    rule_name = Column(
        String(100),
        nullable=False,
        comment="Nombre descriptivo de la regla"
    )
    
    matching_criteria = Column(
        JSONB,
        nullable=False,
        comment="Criterios de coincidencia (keywords, amounts, vendors)"
    )
    
    enabled = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Si la regla está activa"
    )
    
    times_applied = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Número de veces aplicada"
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="category_rules"
    )
    
    category = relationship(
        "Category",
        back_populates="rules"
    )
    
    def __repr__(self) -> str:
        return f"<CategoryRule(id={self.id}, name={self.rule_name}, enabled={self.enabled})>"
    
    def increment_applied(self) -> None:
        """Increment times_applied counter"""
        self.times_applied += 1