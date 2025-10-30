"""
Repositorio para cuentas bancarias.
"""

from typing import List, Optional
from uuid import UUID

from app.models.bank_account import BankAccount
from app.repositories.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BankAccountRepository(BaseRepository[BankAccount]):
    """Repositorio especializado para cuentas bancarias."""

    def __init__(self, db: AsyncSession):
        """Inicializa el repositorio con la sesión de base de datos."""
        super().__init__(BankAccount, db)

    async def list_by_user(self, user_id: UUID) -> List[BankAccount]:
        """Obtiene todas las cuentas pertenecientes a un usuario."""
        result = await self.db.execute(
            select(BankAccount)
            .where(BankAccount.user_id == user_id)
            .order_by(BankAccount.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_by_id_for_user(
        self,
        account_id: UUID,
        user_id: UUID,
    ) -> Optional[BankAccount]:
        """Obtiene una cuenta por ID validando que pertenezca al usuario."""
        result = await self.db.execute(
            select(BankAccount).where(
                (BankAccount.id == account_id)
                & (BankAccount.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name_for_user(
        self,
        name: str,
        user_id: UUID,
    ) -> Optional[BankAccount]:
        """Obtiene una cuenta por nombre dentro del contexto de un usuario."""
        result = await self.db.execute(
            select(BankAccount).where(
                (BankAccount.name == name)
                & (BankAccount.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def delete_for_user(self, account_id: UUID, user_id: UUID) -> bool:
        """Elimina una cuenta validando pertenencia."""
        account = await self.get_by_id_for_user(account_id, user_id)
        if account is None:
            return False

        await self.db.delete(account)
        await self.db.commit()
        return True
