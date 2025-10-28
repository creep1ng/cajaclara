"""Configuración de conexión y sesiones SQLAlchemy.

Esta implementación usa la variable de entorno `DATABASE_URL`. Si no está
definida, cae a SQLite local para desarrollo (`sqlite:///./dev.db`).

Exporta `engine`, `SessionLocal` y helper `get_db` para usar desde servicios
o endpoints.
"""
import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Prefer Postgres in production. Fallback to local Postgres connection for dev if env var missing.
# Example docker-compose service might provide: postgresql://postgres:postgres@db:5432/cajaclara
DATABASE_URL = os.getenv(
	"DATABASE_URL",
	"postgresql://postgres:postgres@localhost:5432/cajaclara",
)

# Create engine with sensible defaults. For SQLite special args would be needed, but this
# project targets Postgres per requirements.
engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@contextmanager
def get_db() -> Iterator:
	"""Context manager simple para obtener una sesión y cerrarla.

	Uso:
		with get_db() as db:
			...
	"""
	db = SessionLocal()
	try:
		yield db
		db.commit()
	except Exception:
		db.rollback()
		raise
	finally:
		db.close()

