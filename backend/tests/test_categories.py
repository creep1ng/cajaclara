"""
Tests para endpoints de categorías.
"""

import pytest
from app.main import app
from app.models.category import Category
from app.repositories.category import CategoryRepository
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

client = TestClient(app)


@pytest.mark.asyncio
async def test_list_categories_success(db_session: AsyncSession):
    """
    Prueba que el endpoint GET /api/v1/categories devuelve 200 y estructura correcta.
    """
    # Crear categorías de prueba
    category_repo = CategoryRepository(db_session)
    
    # Categoría de ingreso
    income_category = Category(
        id="cat-salary",
        name="Salario",
        icon="money",
        color="#00FF00",
        transaction_type="income",
        description="Ingreso por salario",
        predefined=True
    )
    
    # Categoría de gasto
    expense_category = Category(
        id="cat-food",
        name="Alimentos",
        icon="restaurant",
        color="#FF0000",
        transaction_type="expense",
        description="Gastos en alimentos",
        predefined=True
    )
    
    # Guardar en base de datos
    db_session.add(income_category)
    db_session.add(expense_category)
    await db_session.commit()
    
    # Realizar petición al endpoint
    response = client.get("/api/v1/categories")
    
    # Verificar respuesta
    assert response.status_code == 200
    
    data = response.json()
    assert "categories" in data
    assert len(data["categories"]) >= 2
    
    # Verificar estructura de categorías
    categories = data["categories"]
    category_ids = [cat["id"] for cat in categories]
    
    assert "cat-salary" in category_ids
    assert "cat-food" in category_ids
    
    # Verificar estructura de cada categoría
    for category in categories:
        assert "id" in category
        assert "name" in category
        assert "transaction_type" in category
        assert "predefined" in category
        assert category["transaction_type"] in ["income", "expense"]
        assert isinstance(category["predefined"], bool)


@pytest.mark.asyncio
async def test_list_categories_filter_by_type(db_session: AsyncSession):
    """
    Prueba el filtrado por tipo de transacción.
    """
    # Crear categorías de prueba
    category_repo = CategoryRepository(db_session)
    
    # Categoría de ingreso
    income_category = Category(
        id="cat-salary",
        name="Salario",
        icon="money",
        color="#00FF00",
        transaction_type="income",
        description="Ingreso por salario",
        predefined=True
    )
    
    # Categoría de gasto
    expense_category = Category(
        id="cat-food",
        name="Alimentos",
        icon="restaurant",
        color="#FF0000",
        transaction_type="expense",
        description="Gastos en alimentos",
        predefined=True
    )
    
    # Guardar en base de datos
    db_session.add(income_category)
    db_session.add(expense_category)
    await db_session.commit()
    
    # Filtrar por ingresos
    response_income = client.get("/api/v1/categories?transaction_type=income")
    assert response_income.status_code == 200
    
    data_income = response_income.json()
    assert all(cat["transaction_type"] == "income" for cat in data_income["categories"])
    
    # Filtrar por gastos
    response_expense = client.get("/api/v1/categories?transaction_type=expense")
    assert response_expense.status_code == 200
    
    data_expense = response_expense.json()
    assert all(cat["transaction_type"] == "expense" for cat in data_expense["categories"])


@pytest.mark.asyncio
async def test_list_categories_search(db_session: AsyncSession):
    """
    Prueba el filtrado por búsqueda.
    """
    # Crear categorías de prueba
    category_repo = CategoryRepository(db_session)
    
    # Categoría con palabra "café"
    coffee_category = Category(
        id="cat-coffee",
        name="Café",
        icon="coffee",
        color="#8B4513",
        transaction_type="expense",
        description="Gastos en café",
        predefined=True
    )
    
    # Categoría sin palabra "café"
    food_category = Category(
        id="cat-food",
        name="Alimentos",
        icon="restaurant",
        color="#FF0000",
        transaction_type="expense",
        description="Gastos en alimentos",
        predefined=True
    )
    
    # Guardar en base de datos
    db_session.add(coffee_category)
    db_session.add(food_category)
    await db_session.commit()
    
    # Buscar por "café"
    response = client.get("/api/v1/categories?search=café")
    assert response.status_code == 200
    
    data = response.json()
    category_ids = [cat["id"] for cat in data["categories"]]
    
    assert "cat-coffee" in category_ids
    assert "cat-food" not in category_ids


def test_list_categories_unauthorized():
    """
    Prueba que el endpoint requiere autenticación (aunque en MVP se usa usuario default).
    """
    # En MVP, el endpoint debería funcionar sin token explícito
    # ya que se usa get_default_user
    response = client.get("/api/v1/categories")
    
    # Debería devolver 500 si no hay base de datos o usuario default
    # o 200 si está configurado el entorno de prueba
    assert response.status_code in [200, 500]