"""
Modelo de categorías para clasificación de transacciones.
"""

from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Category(Base, TimestampMixin):
    """Modelo de categoría"""

    __tablename__ = "categories"
    __table_args__ = ({"comment": "Categorías para clasificación de transacciones"},)

    id = Column(String(50), primary_key=True, comment="ID de categoría (ej: cat-cafe)")

    name = Column(String(100), nullable=False, comment="Nombre de la categoría")

    icon = Column(String(50), nullable=True, comment="Código de icono para UI")

    color = Column(String(7), nullable=True, comment="Color hexadecimal (#RRGGBB)")

    transaction_type = Column(
        String(20), nullable=False, index=True, comment="Tipo: income o expense"
    )

    description = Column(Text, nullable=True, comment="Descripción de la categoría")

    predefined = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Si es categoría del sistema o personalizada",
    )

    # Relationships
    transactions = relationship("Transaction", back_populates="category")

    rules = relationship(
        "CategoryRule", back_populates="category", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Category(id={self.id}, name={self.name}, type={self.transaction_type})>"
        )
