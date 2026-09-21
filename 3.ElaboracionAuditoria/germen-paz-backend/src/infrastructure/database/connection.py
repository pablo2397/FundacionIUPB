"""Conexión síncrona a SQLite vía SQLAlchemy.

Decisión de diseño (síncrono vs asíncrono): se elige un diseño
**síncrono** para este MVP. SQLite + `aiosqlite` no aporta beneficios
reales de concurrencia (SQLite serializa escrituras a nivel de
archivo de todas formas) y el driver síncrono de SQLAlchemy es más
simple de testear con `TestClient`/mocks y más maduro en cuanto a
herramientas (Alembic, etc.). Si el proyecto evoluciona a Postgres
con alta concurrencia, se recomienda migrar a SQLAlchemy async.
"""
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.infrastructure.config.settings import get_settings

settings = get_settings()

# check_same_thread=False es necesario porque FastAPI puede usar la
# conexión desde distintos hilos del pool; SQLAlchemy gestiona el
# acceso seguro a través del sessionmaker/scoped session por request.
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """Dependencia de FastAPI: entrega una sesión de DB por request y la cierra al final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
