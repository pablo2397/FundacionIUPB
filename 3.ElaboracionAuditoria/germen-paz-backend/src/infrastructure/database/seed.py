"""Seed inicial: crea el usuario admin si aún no existe.

Se ejecuta en el evento `startup` de FastAPI (ver `main.py`). Las
credenciales del admin se leen desde `.env` (`ADMIN_USERNAME`,
`ADMIN_EMAIL`, `ADMIN_PASSWORD`), nunca se hardcodean.
"""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from src.domain.entities.user import UserRole
from src.infrastructure.config.settings import Settings
from src.infrastructure.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from src.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from src.domain.entities.user import User

logger = logging.getLogger("germen_paz.seed")


def seed_admin_user(db: Session, settings: Settings) -> None:
    repository = SqlAlchemyUserRepository(db)
    existing = repository.get_by_username(settings.ADMIN_USERNAME)
    if existing is not None:
        logger.info("Usuario admin ya existe, se omite el seed.")
        return

    hasher = BcryptPasswordHasher()
    admin = User(
        id=None,
        username=settings.ADMIN_USERNAME,
        email=settings.ADMIN_EMAIL,
        hashed_password=hasher.hash(settings.ADMIN_PASSWORD),
        role=UserRole.ADMIN,
    )
    repository.create(admin)
    logger.info("Usuario admin inicial creado: %s", settings.ADMIN_USERNAME)
