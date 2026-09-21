"""Entidad de dominio: Usuario.

Clase pura, sin dependencias de frameworks ni de infraestructura
(ni SQLAlchemy, ni Pydantic). Representa las reglas de negocio del
usuario dentro del sistema.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """Roles soportados por el sistema (RBAC)."""

    ADMIN = "admin"
    OPERADOR = "operador"


@dataclass
class User:
    """Entidad de usuario del dominio.

    `hashed_password` nunca contiene la contraseña en texto plano;
    el hashing es responsabilidad de la capa de infraestructura
    (ver `application/interfaces/password_hasher.py`).
    """

    id: int | None
    username: str
    email: str
    hashed_password: str
    role: UserRole
    is_active: bool = True
    created_at: datetime | None = None

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def can_delete_products(self) -> bool:
        """Regla de negocio: solo el admin puede eliminar productos."""
        return self.role == UserRole.ADMIN

    def can_write_products(self) -> bool:
        """Regla de negocio: admin y operador pueden crear/actualizar."""
        return self.role in (UserRole.ADMIN, UserRole.OPERADOR)
