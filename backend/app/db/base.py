"""Base declarativa para los modelos SQLAlchemy.

Se expone `Base` para que los modelos la importen y `metadata` para usos
automatizados (migraciones, tests).
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
metadata = Base.metadata

