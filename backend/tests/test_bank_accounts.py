"""
Tests para funcionalidad de cuentas bancarias.
"""

from decimal import Decimal
from uuid import uuid4

import pytest
from app.models.bank_account import BankAccount
from app.models.user import User
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestBankAccountsEndpoints:
    """Tests para endpoints de cuentas bancarias"""
    
    @pytest.mark.asyncio
    async def test_create_bank_account_success(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """Test crear cuenta bancaria exitosamente"""
        payload = {
            "name": "Cuenta Nómina",
            "color": "#1ABC9C",
            "initial_balance": 500000.00
        }
        
        response = await client.post(
            "/api/v1/bank-accounts",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Cuenta Nómina"
        assert data["color"] == "#1ABC9C"
        assert float(data["initial_balance"]) == 500000.00
        assert float(data["current_balance"]) == 500000.00
        assert data["user_id"] == str(test_user.id)
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    @pytest.mark.asyncio
    async def test_create_bank_account_with_current_balance(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict
    ):
        """Test crear cuenta con saldo actual diferente al inicial"""
        payload = {
            "name": "Cuenta Ahorros",
            "color": "#E74C3C",
            "initial_balance": 1000000.00,
            "current_balance": 850000.00
        }
        
        response = await client.post(
            "/api/v1/bank-accounts",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert float(data["initial_balance"]) == 1000000.00
        assert float(data["current_balance"]) == 850000.00
    
    @pytest.mark.asyncio
    async def test_create_bank_account_invalid_color(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test crear cuenta con color inválido"""
        payload = {
            "name": "Test Account",
            "color": "red",  # Formato inválido
            "initial_balance": 100000.00
        }
        
        response = await client.post(
            "/api/v1/bank-accounts",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_bank_account_negative_balance(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test crear cuenta con saldo negativo"""
        payload = {
            "name": "Test Account",
            "color": "#000000",
            "initial_balance": -1000.00
        }
        
        response = await client.post(
            "/api/v1/bank-accounts",
            json=payload,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_list_bank_accounts(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db: AsyncSession
    ):
        """Test listar cuentas bancarias del usuario"""
        # Crear algunas cuentas de prueba
        accounts = [
            BankAccount(
                user_id=test_user.id,
                name=f"Cuenta {i}",
                color="#FF0000",
                initial_balance=Decimal(str(100000.00 * i)),
                current_balance=Decimal(str(100000.00 * i))
            )
            for i in range(1, 4)
        ]
        
        for account in accounts:
            db.add(account)
        await db.commit()
        
        response = await client.get(
            "/api/v1/bank-accounts",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "accounts" in data
        assert "total" in data
        assert data["total"] == 3
        assert len(data["accounts"]) == 3
    
    @pytest.mark.asyncio
    async def test_get_bank_account_success(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db: AsyncSession
    ):
        """Test obtener cuenta bancaria específica"""
        account = BankAccount(
            user_id=test_user.id,
            name="Mi Cuenta",
            color="#00FF00",
            initial_balance=Decimal("250000.00"),
            current_balance=Decimal("200000.00")
        )
        db.add(account)
        await db.commit()
        await db.refresh(account)
        
        response = await client.get(
            f"/api/v1/bank-accounts/{account.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(account.id)
        assert data["name"] == "Mi Cuenta"
        assert data["color"] == "#00FF00"
    
    @pytest.mark.asyncio
    async def test_get_bank_account_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test obtener cuenta que no existe"""
        fake_id = uuid4()
        
        response = await client.get(
            f"/api/v1/bank-accounts/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_bank_account_success(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db: AsyncSession
    ):
        """Test actualizar cuenta bancaria"""
        account = BankAccount(
            user_id=test_user.id,
            name="Cuenta Original",
            color="#0000FF",
            initial_balance=Decimal("300000.00"),
            current_balance=Decimal("300000.00")
        )
        db.add(account)
        await db.commit()
        await db.refresh(account)
        
        update_payload = {
            "name": "Cuenta Actualizada",
            "color": "#FFFF00",
            "current_balance": 280000.00
        }
        
        response = await client.put(
            f"/api/v1/bank-accounts/{account.id}",
            json=update_payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Cuenta Actualizada"
        assert data["color"] == "#FFFF00"
        assert float(data["current_balance"]) == 280000.00
        assert float(data["initial_balance"]) == 300000.00  # No cambia
    
    @pytest.mark.asyncio
    async def test_update_bank_account_partial(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db: AsyncSession
    ):
        """Test actualización parcial de cuenta"""
        account = BankAccount(
            user_id=test_user.id,
            name="Cuenta Test",
            color="#AABBCC",
            initial_balance=Decimal("100000.00"),
            current_balance=Decimal("100000.00")
        )
        db.add(account)
        await db.commit()
        await db.refresh(account)
        
        update_payload = {
            "name": "Nuevo Nombre"
        }
        
        response = await client.put(
            f"/api/v1/bank-accounts/{account.id}",
            json=update_payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Nuevo Nombre"
        assert data["color"] == "#AABBCC"  # Sin cambios
    
    @pytest.mark.asyncio
    async def test_delete_bank_account_success(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        db: AsyncSession
    ):
        """Test eliminar cuenta bancaria"""
        account = BankAccount(
            user_id=test_user.id,
            name="Cuenta a Eliminar",
            color="#123456",
            initial_balance=Decimal("50000.00"),
            current_balance=Decimal("50000.00")
        )
        db.add(account)
        await db.commit()
        await db.refresh(account)
        
        response = await client.delete(
            f"/api/v1/bank-accounts/{account.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verificar que ya no existe
        get_response = await client.get(
            f"/api/v1/bank-accounts/{account.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_bank_account_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test eliminar cuenta que no existe"""
        fake_id = uuid4()
        
        response = await client.delete(
            f"/api/v1/bank-accounts/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_user_isolation(
        self,
        client: AsyncClient,
        test_user: User,
        db: AsyncSession
    ):
        """Test que usuarios no pueden ver cuentas de otros usuarios"""
        # Crear otro usuario
        other_user = User(
            email="other@example.com",
            hashed_password="hashedpass",
            full_name="Other User"
        )
        db.add(other_user)
        await db.commit()
        await db.refresh(other_user)
        
        # Crear cuenta para el otro usuario
        other_account = BankAccount(
            user_id=other_user.id,
            name="Cuenta Privada",
            color="#ABCDEF",
            initial_balance=Decimal("999999.00"),
            current_balance=Decimal("999999.00")
        )
        db.add(other_account)
        await db.commit()
        await db.refresh(other_account)
        
        # Intentar acceder con el test_user
        # (Aquí necesitarías implementar la lógica de auth_headers para test_user)
        # Este test es un placeholder para mostrar la importancia de la aislación


class TestBankAccountService:
    """Tests unitarios para el servicio de cuentas bancarias"""
    
    @pytest.mark.asyncio
    async def test_create_account_sets_current_balance_from_initial(
        self,
        db: AsyncSession,
        test_user: User
    ):
        """Test que current_balance se inicializa con initial_balance si no se provee"""
        from app.repositories.bank_account import BankAccountRepository
        from app.schemas.bank_account import CreateBankAccountRequest
        from app.services.bank_account_service import BankAccountService
        
        repo = BankAccountRepository(db)
        service = BankAccountService(repo)
        
        request = CreateBankAccountRequest(
            name="Test Account",
            color="#FF0000",
            initial_balance=Decimal("100000.00")
        )
        
        result = await service.create_account(test_user.id, request)
        
        assert result.initial_balance == Decimal("100000.00")
        assert result.current_balance == Decimal("100000.00")
    
    @pytest.mark.asyncio
    async def test_validate_color_format(self, db: AsyncSession, test_user: User):
        """Test validación de formato de color hexadecimal"""
        from app.core.exceptions import ValidationError
        from app.repositories.bank_account import BankAccountRepository
        from app.schemas.bank_account import CreateBankAccountRequest
        from app.services.bank_account_service import BankAccountService
        
        repo = BankAccountRepository(db)
        service = BankAccountService(repo)
        
        request = CreateBankAccountRequest(
            name="Test",
            color="red",  # Formato inválido
            initial_balance=Decimal("100.00")
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await service.create_account(test_user.id, request)
        
        assert exc_info.value.code == "BANK_ACCOUNT_INVALID_COLOR"
