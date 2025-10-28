from __future__ import annotations

import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, Numeric, String
from sqlalchemy.sql import func

from backend.app.db.base import Base


class TransactionType(str):
	INCOME = "income"
	EXPENSE = "expense"


class SyncStatus(str):
	PENDING = "pending"
	SYNCED = "synced"
	FAILED = "failed"


class Transaction(Base):
	__tablename__ = "transactions"

	id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
	user_id = Column(String(36), nullable=False, index=True)
	client_id = Column(String(80), nullable=True, index=True)

	transaction_type = Column(Enum(TransactionType), nullable=False)
	amount = Column(Numeric(14, 2), nullable=False)
	currency = Column(String(3), nullable=False, default="COP")

	category_id = Column(String(80), nullable=False)
	account_id = Column(String(80), nullable=False, index=True)

	description = Column(String(500), nullable=True)
	recipient = Column(String(200), nullable=True)
	classification = Column(String(20), nullable=True)

	transaction_date = Column(DateTime(timezone=True), nullable=False, default=func.now())

	sync_status = Column(Enum(SyncStatus), nullable=False, default=SyncStatus.SYNCED)

	metadata = Column(JSON, nullable=True)
	deleted = Column(Boolean, nullable=False, default=False)

	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
	updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

	def to_dict(self) -> dict:
		return {
			"id": self.id,
			"client_id": self.client_id,
			"user_id": self.user_id,
			"transaction_type": self.transaction_type,
			"amount": float(self.amount) if self.amount is not None else None,
			"currency": self.currency,
			"category_id": self.category_id,
			"account_id": self.account_id,
			"description": self.description,
			"recipient": self.recipient,
			"classification": self.classification,
			"transaction_date": self.transaction_date.isoformat() if self.transaction_date else None,
			"sync_status": self.sync_status,
			"metadata": self.metadata,
			"deleted": self.deleted,
			"created_at": self.created_at.isoformat() if self.created_at else None,
			"updated_at": self.updated_at.isoformat() if self.updated_at else None,
		}

