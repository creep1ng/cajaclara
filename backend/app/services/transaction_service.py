"""Lógica de negocio para transacciones.

Provee funciones para crear transacciones, sincronizar lotes enviados desde el
cliente (offline-first) y calcular saldos por cuenta.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Union

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.transaction import SyncStatus, Transaction, TransactionType
from backend.app.schemas.transaction import TransactionCreate


class TransactionValidationError(ValueError):
    pass


def _validate_payload(payload: Dict[str, Any]) -> None:
    # Required fields
    required = ["amount", "category_id", "account_id", "transaction_type", "transaction_date"]
    for k in required:
        if k not in payload:
            raise TransactionValidationError(f"Campo requerido faltante: {k}")

    # Amount validation
    try:
        amount = Decimal(str(payload["amount"]))
    except Exception:
        raise TransactionValidationError("El monto debe ser numérico")

    if amount <= 0:
        raise TransactionValidationError("El monto debe ser mayor a 0")

    # Type validation
    if payload.get("transaction_type") not in (TransactionType.INCOME, TransactionType.EXPENSE):
        raise TransactionValidationError("Tipo de transacción inválido")


def create_transaction(db: Session, user_id: str, payload: Union[Dict[str, Any], TransactionCreate]) -> Transaction:
    """Crea una transacción y retorna la instancia persistida.

    - `payload` es un dict que contiene los campos esperados por el API.
    - La función no hace commit; asume que el caller gestiona la transacción/commit
      (ej. usando el context manager `get_db`).
    """
    # Accept Pydantic model or raw dict
    if isinstance(payload, TransactionCreate):
        payload_data = payload.dict()
    else:
        payload_data = payload

    _validate_payload(payload_data)

    t = Transaction(
        user_id=user_id,
        client_id=payload_data.get("client_id"),
        transaction_type=payload_data["transaction_type"],
        amount=Decimal(str(payload_data["amount"])),
        currency=payload_data.get("currency", "COP"),
        category_id=payload_data["category_id"],
        account_id=payload_data["account_id"],
        description=payload_data.get("description") or payload_data.get("note"),
        recipient=payload_data.get("recipient"),
        classification=payload_data.get("classification"),
        transaction_date=payload_data.get("transaction_date"),
        sync_status=SyncStatus.SYNCED,
        metadata=payload_data.get("metadata"),
    )

    db.add(t)
    # flush to populate t.id without committing
    db.flush()
    return t


def get_account_balance(db: Session, user_id: str, account_id: str) -> Decimal:
    """Calcula el balance neto de una cuenta para un usuario.

    Income suma, expense resta. Ignora transacciones marcadas como `deleted`.
    """
    stmt_income = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.user_id == user_id,
        Transaction.account_id == account_id,
        Transaction.transaction_type == TransactionType.INCOME,
    Transaction.deleted.is_(False),
    )
    stmt_expense = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.user_id == user_id,
        Transaction.account_id == account_id,
        Transaction.transaction_type == TransactionType.EXPENSE,
    Transaction.deleted.is_(False),
    )

    income = db.execute(stmt_income).scalar_one()
    expense = db.execute(stmt_expense).scalar_one()

    # income and expense can be Decimal or numeric -> cast to Decimal
    return Decimal(income) - Decimal(expense)


def sync_transactions(db: Session, user_id: str, items: List[Union[Dict[str, Any], TransactionCreate]]) -> Dict[str, Any]:
    """Procesa una lista de transacciones enviadas por el cliente en modo offline.

    Retorna un dict con `results` por item y `balances` actualizado por account.
    """
    results = []
    touched_accounts: Dict[str, bool] = {}

    for item in items:
        # accept Pydantic or dict
        if isinstance(item, TransactionCreate):
            item_data = item.dict()
        else:
            item_data = item

        client_id = item_data.get("client_id")
        # Deduplicación por client_id (si existe)
        if client_id:
            existing = db.execute(
                select(Transaction).where(Transaction.user_id == user_id, Transaction.client_id == client_id)
            ).scalar_one_or_none()
            if existing:
                results.append({"client_id": client_id, "status": "duplicate", "server_id": existing.id})
                touched_accounts[existing.account_id] = True
                continue

        try:
            t = create_transaction(db, user_id, item_data)
            results.append({"client_id": client_id, "status": "created", "server_id": t.id})
            touched_accounts[t.account_id] = True
        except TransactionValidationError as e:
            results.append({"client_id": client_id, "status": "error", "error": str(e)})

    # Calcular balances para cuentas tocadas
    balances: Dict[str, str] = {}
    for account_id in touched_accounts.keys():
        bal = get_account_balance(db, user_id, account_id)
        balances[account_id] = str(bal)

    return {"results": results, "balances": balances}
# Lógica de negocio para transacciones
# ...existing code...
