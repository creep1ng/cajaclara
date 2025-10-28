from __future__ import annotations

from sqlalchemy import Column, String

from backend.app.db.base import Base


class User(Base):
	__tablename__ = "users"

	id = Column(String(36), primary_key=True)
	name = Column(String(200), nullable=True)
	email = Column(String(200), nullable=True, unique=True)

