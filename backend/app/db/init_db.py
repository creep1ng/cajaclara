"""
Inicialización de base de datos con datos por defecto.
"""

from uuid import UUID

from app.config import settings
from app.models.bank_account import BankAccount
from app.models.category import Category
from app.models.user import User
from app.utils.auth import hash_password
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def init_db(db: AsyncSession) -> None:
    """
    Inicializa la base de datos con datos por defecto.
    
    Args:
        db: Sesión de base de datos
    """
    print("🔧 Inicializando base de datos...")
    
    # Crear usuario default si no existe
    await create_default_user(db)
    
    # Seed de categorías
    await seed_categories(db)
    
    # Seed de cuentas bancarias
    await seed_bank_accounts(db)
    
    print("✅ Base de datos inicializada correctamente")


async def create_default_user(db: AsyncSession) -> None:
    """Crea usuario default para MVP"""
    result = await db.execute(
        select(User).where(User.id == UUID(settings.DEFAULT_USER_ID))
    )
    default_user = result.scalar_one_or_none()

    if default_user is None:
        default_user = User(
            id=UUID(settings.DEFAULT_USER_ID),
            email=settings.DEFAULT_USER_EMAIL,
            hashed_password=hash_password(settings.DEFAULT_USER_PASSWORD),
            full_name="Usuario Demo",
            is_active=True
        )
        db.add(default_user)
        await db.commit()
        print(f"✓ Usuario default creado: {settings.DEFAULT_USER_EMAIL}")
    else:
        # Si el usuario existe pero tiene la contraseña placeholder, actualizarla
        if default_user.hashed_password == "not-used-in-mvp":
            default_user.hashed_password = hash_password(settings.DEFAULT_USER_PASSWORD)
            await db.commit()
            print(f"✓ Usuario default actualizado con nueva contraseña: {settings.DEFAULT_USER_EMAIL}")
        else:
            print(f"✓ Usuario default ya existe: {settings.DEFAULT_USER_EMAIL}")


async def seed_categories(db: AsyncSession) -> None:
    """Crea categorías predefinidas si no existen"""
    result = await db.execute(select(Category))
    existing = result.scalars().all()
    
    if len(existing) > 0:
        print(f"✓ Categorías ya existen ({len(existing)} categorías)")
        return
    
    categories = [
        # Gastos
        {
            "id": "cat-food",
            "name": "Alimentación",
            "icon": "🍔",
            "color": "#FF6B6B",
            "transaction_type": "expense",
            "description": "Compras de alimentos y supermercado",
            "predefined": True
        },
        {
            "id": "cat-transport",
            "name": "Transporte",
            "icon": "🚗",
            "color": "#4ECDC4",
            "transaction_type": "expense",
            "description": "Transporte público, gasolina, Uber",
            "predefined": True
        },
        {
            "id": "cat-utilities",
            "name": "Servicios",
            "icon": "💡",
            "color": "#45B7D1",
            "transaction_type": "expense",
            "description": "Luz, agua, internet, teléfono",
            "predefined": True
        },
        {
            "id": "cat-rent",
            "name": "Arriendo",
            "icon": "🏠",
            "color": "#96CEB4",
            "transaction_type": "expense",
            "description": "Pago de arriendo o hipoteca",
            "predefined": True
        },
        {
            "id": "cat-entertainment",
            "name": "Entretenimiento",
            "icon": "🎬",
            "color": "#FFEAA7",
            "transaction_type": "expense",
            "description": "Cine, streaming, eventos",
            "predefined": True
        },
        {
            "id": "cat-health",
            "name": "Salud",
            "icon": "⚕️",
            "color": "#DFE6E9",
            "transaction_type": "expense",
            "description": "Médico, medicamentos, seguros",
            "predefined": True
        },
        {
            "id": "cat-education",
            "name": "Educación",
            "icon": "📚",
            "color": "#74B9FF",
            "transaction_type": "expense",
            "description": "Cursos, libros, materiales",
            "predefined": True
        },
        {
            "id": "cat-shopping",
            "name": "Compras",
            "icon": "🛍️",
            "color": "#A29BFE",
            "transaction_type": "expense",
            "description": "Ropa, accesorios, artículos personales",
            "predefined": True
        },
        {
            "id": "cat-cafe",
            "name": "Café/Restaurante",
            "icon": "☕",
            "color": "#FD79A8",
            "transaction_type": "expense",
            "description": "Cafeterías, restaurantes, comida fuera",
            "predefined": True
        },
        {
            "id": "cat-other-expense",
            "name": "Otros Gastos",
            "icon": "📦",
            "color": "#B2BEC3",
            "transaction_type": "expense",
            "description": "Gastos varios no categorizados",
            "predefined": True
        },
        
        # Ingresos
        {
            "id": "cat-salary",
            "name": "Salario",
            "icon": "💰",
            "color": "#00B894",
            "transaction_type": "income",
            "description": "Salario mensual o quincenal",
            "predefined": True
        },
        {
            "id": "cat-freelance",
            "name": "Freelance",
            "icon": "💼",
            "color": "#00CEC9",
            "transaction_type": "income",
            "description": "Trabajos independientes y proyectos",
            "predefined": True
        },
        {
            "id": "cat-sales",
            "name": "Ventas",
            "icon": "🏪",
            "color": "#FDCB6E",
            "transaction_type": "income",
            "description": "Ventas de productos o servicios",
            "predefined": True
        },
        {
            "id": "cat-investment",
            "name": "Inversiones",
            "icon": "📈",
            "color": "#6C5CE7",
            "transaction_type": "income",
            "description": "Rendimientos de inversiones",
            "predefined": True
        },
        {
            "id": "cat-other-income",
            "name": "Otros Ingresos",
            "icon": "💵",
            "color": "#55EFC4",
            "transaction_type": "income",
            "description": "Ingresos varios no categorizados",
            "predefined": True
        },
    ]
    
    for cat_data in categories:
        category = Category(**cat_data)
        db.add(category)
    
    await db.commit()
    print(f"✓ {len(categories)} categorías creadas")


async def seed_bank_accounts(db: AsyncSession) -> None:
    """Crea cuentas bancarias por defecto para el usuario demo si no existen"""
    result = await db.execute(
        select(BankAccount).where(BankAccount.user_id == UUID(settings.DEFAULT_USER_ID))
    )
    existing = result.scalars().all()
    
    if len(existing) > 0:
        print(f"✓ Cuentas bancarias ya existen ({len(existing)} cuentas)")
        return
    
    # Obtener el usuario default
    user_result = await db.execute(
        select(User).where(User.id == UUID(settings.DEFAULT_USER_ID))
    )
    default_user = user_result.scalar_one_or_none()
    
    if default_user is None:
        print("⚠ Usuario default no encontrado, no se pueden crear cuentas bancarias")
        return
    
    bank_accounts = [
        {
            "user_id": UUID(settings.DEFAULT_USER_ID),
            "name": "Ahorros",
            "color": "#00B894",
            "initial_balance": 500000.00,
            "current_balance": 500000.00
        },
        {
            "user_id": UUID(settings.DEFAULT_USER_ID),
            "name": "Tarjeta Débito",
            "color": "#4ECDC4",
            "initial_balance": 1200000.00,
            "current_balance": 1200000.00
        },
        {
            "user_id": UUID(settings.DEFAULT_USER_ID),
            "name": "Efectivo",
            "color": "#FFD93D",
            "initial_balance": 150000.00,
            "current_balance": 150000.00
        },
    ]
    
    for account_data in bank_accounts:
        bank_account = BankAccount(**account_data)
        db.add(bank_account)
    
    await db.commit()
    print(f"✓ {len(bank_accounts)} cuentas bancarias creadas para usuario demo")