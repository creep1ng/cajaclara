"""
Clase base para todos los modelos SQLAlchemy.
Incluye campos comunes y utilidades.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Clase base para todos los modelos"""

    pass


class TimestampMixin:
    """Mixin para campos de timestamp"""

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Fecha de creación",
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Fecha de última actualización",
    )


class UUIDMixin:
    """Mixin para ID UUID"""

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="Identificador único",
    )


class SoftDeleteMixin:
    """Mixin para soft delete"""

    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de eliminación (soft delete)",
    )

    @property
    def is_deleted(self) -> bool:
        """Check if record is soft deleted"""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Mark record as deleted"""
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore soft deleted record"""
        self.deleted_at = None


class AuditMixin:
    """Mixin para auditoría de cambios"""

    @declared_attr
    def created_by(cls):
        return Column(
            UUID(as_uuid=True), nullable=True, comment="Usuario que creó el registro"
        )

    @declared_attr
    def updated_by(cls):
        return Column(
            UUID(as_uuid=True),
            nullable=True,
            comment="Usuario que actualizó el registro",
        )
