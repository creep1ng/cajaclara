"""
Repositorio para transacciones.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from app.models.transaction import Transaction
from app.repositories.base import BaseRepository
from app.schemas.transaction import TransactionFilters, TransactionSummary
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class TransactionRepository(BaseRepository[Transaction]):
    """Repositorio para operaciones de transacciones"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Transaction, db)
    
    async def get_by_id_with_category(
        self,
        transaction_id: UUID,
        user_id: UUID
    ) -> Optional[Transaction]:
        """
        Obtiene transacción con categoría cargada.
        
        Args:
            transaction_id: UUID de la transacción
            user_id: UUID del usuario propietario
            
        Returns:
            Transacción con categoría o None
        """
        result = await self.db.execute(
            select(Transaction)
            .options(selectinload(Transaction.category))
            .where(
                and_(
                    Transaction.id == transaction_id,
                    Transaction.user_id == user_id,
                    Transaction.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def list_with_filters(
        self,
        user_id: UUID,
        filters: TransactionFilters,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Transaction], int]:
        """
        Lista transacciones con filtros y paginación.
        
        Args:
            user_id: UUID del usuario
            filters: Filtros a aplicar
            skip: Registros a saltar
            limit: Máximo de registros
            
        Returns:
            Tupla (lista de transacciones, total de registros)
        """
        # Build query conditions
        conditions = [
            Transaction.user_id == user_id,
            Transaction.deleted_at.is_(None)
        ]
        
        if filters.start_date:
            conditions.append(Transaction.transaction_date >= filters.start_date)
        
        if filters.end_date:
            conditions.append(Transaction.transaction_date <= filters.end_date)
        
        if filters.transaction_type:
            conditions.append(Transaction.transaction_type == filters.transaction_type)
        
        if filters.classification:
            conditions.append(Transaction.classification == filters.classification)
        
        if filters.category_id:
            conditions.append(Transaction.category_id == filters.category_id)
        
        if filters.entrepreneurship_id:
            conditions.append(Transaction.entrepreneurship_id == filters.entrepreneurship_id)
        
        # Query for transactions
        query = (
            select(Transaction)
            .options(selectinload(Transaction.category))
            .where(and_(*conditions))
            .order_by(Transaction.transaction_date.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(query)
        transactions = list(result.scalars().all())
        
        # Count total
        count_query = select(func.count()).select_from(Transaction).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar_one()
        
        return transactions, total
    
    async def calculate_summary(
        self,
        user_id: UUID,
        filters: TransactionFilters
    ) -> TransactionSummary:
        """
        Calcula resumen de transacciones.
        
        Args:
            user_id: UUID del usuario
            filters: Filtros a aplicar
            
        Returns:
            Resumen con totales
        """
        conditions = [
            Transaction.user_id == user_id,
            Transaction.deleted_at.is_(None)
        ]
        
        if filters.start_date:
            conditions.append(Transaction.transaction_date >= filters.start_date)
        
        if filters.end_date:
            conditions.append(Transaction.transaction_date <= filters.end_date)
        
        if filters.transaction_type:
            conditions.append(Transaction.transaction_type == filters.transaction_type)
        
        if filters.classification:
            conditions.append(Transaction.classification == filters.classification)
        
        if filters.entrepreneurship_id:
            conditions.append(Transaction.entrepreneurship_id == filters.entrepreneurship_id)
        
        # Query aggregations
        query = select(
            Transaction.transaction_type,
            Transaction.classification,
            func.sum(Transaction.amount).label("total")
        ).where(and_(*conditions)).group_by(
            Transaction.transaction_type,
            Transaction.classification
        )
        
        result = await self.db.execute(query)
        rows = result.all()
        
        # Build summary
        summary = TransactionSummary()
        
        for row in rows:
            amount = Decimal(str(row.total)) if row.total else Decimal("0.00")
            
            if row.transaction_type == "income":
                summary.total_income += amount
                if row.classification == "personal":
                    summary.by_classification["personal"].income += amount
                else:
                    summary.by_classification["business"].income += amount
            else:
                summary.total_expense += amount
                if row.classification == "personal":
                    summary.by_classification["personal"].expense += amount
                else:
                    summary.by_classification["business"].expense += amount
        
        summary.net_balance = summary.total_income - summary.total_expense
        
        return summary
    
    async def soft_delete(self, transaction_id: UUID, user_id: UUID) -> bool:
        """
        Soft delete de transacción.
        
        Args:
            transaction_id: UUID de la transacción
            user_id: UUID del usuario propietario
            
        Returns:
            True si se eliminó, False si no existía
        """
        transaction = await self.get_by_id_with_category(transaction_id, user_id)
        if transaction is None:
            return False
        
        transaction.soft_delete()
        await self.db.commit()
        return True