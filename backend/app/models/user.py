"""
Modelo de usuario para autenticación y autorización.
"""

from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """Modelo de usuario"""

    __tablename__ = "users"
    __table_args__ = ({"comment": "Usuarios del sistema"},)

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Email del usuario (único)",
    )

    hashed_password = Column(
        String(255), nullable=False, comment="Contraseña hasheada con bcrypt"
    )

    full_name = Column(
        String(255), nullable=True, comment="Nombre completo del usuario"
    )

    is_active = Column(Boolean, default=True, nullable=False, comment="Usuario activo")

    # Relationships
    transactions = relationship(
        "Transaction",
        back_populates="user",
        foreign_keys="Transaction.user_id",
        cascade="all, delete-orphan",
    )

    entrepreneurships = relationship(
        "Entrepreneurship", back_populates="user", cascade="all, delete-orphan"
    )

    category_rules = relationship(
        "CategoryRule", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
