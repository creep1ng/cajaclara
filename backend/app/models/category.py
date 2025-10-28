from __future__ import annotations

from sqlalchemy import Boolean, Column, String

from backend.app.db.base import Base


class Category(Base):
	__tablename__ = "categories"

	id = Column(String(80), primary_key=True)
	name = Column(String(200), nullable=False)
	transaction_type = Column(String(20), nullable=False)
	description = Column(String(500), nullable=True)
	predefined = Column(Boolean, default=True)

