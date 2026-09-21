"""Caso de uso: registrar un nuevo usuario.

Regla de negocio: el registro solo puede ser ejecutado por un admin
(esto se aplica en la capa `core` vía dependencia `require_role`,
ver `core/dependencies/auth.py`). Este caso de uso asume que la
autorización ya fue verificada por quien lo invoca.
"""
from __future__ import annotations

from src.application.dtos.auth_dto import RegisterUserInput, UserOutput
from src.application.interfaces.password_hasher import PasswordHasher
from src.domain.entities.user import User
from src.domain.exceptions.domain_exceptions import UserAlreadyExistsError
from src.domain.repositories.user_repository import UserRepository


class RegisterUserUseCase:
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher) -> None:
        self._repository = user_repository
        self._hasher = password_hasher

    def execute(self, data: RegisterUserInput) -> UserOutput:
        if self._repository.get_by_username(data.username) is not None:
            raise UserAlreadyExistsError(f"El nombre de usuario '{data.username}' ya existe.")
        if self._repository.get_by_email(data.email) is not None:
            raise UserAlreadyExistsError(f"El email '{data.email}' ya está registrado.")

        user = User(
            id=None,
            username=data.username,
            email=data.email,
            hashed_password=self._hasher.hash(data.password),
            role=data.role,
        )
        created = self._repository.create(user)
        return UserOutput(
            id=created.id,  # type: ignore[arg-type]
            username=created.username,
            email=created.email,
            role=created.role,
            is_active=created.is_active,
        )
