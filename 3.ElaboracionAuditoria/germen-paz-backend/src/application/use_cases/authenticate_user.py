"""Caso de uso: autenticar un usuario (login) y emitir un JWT.

Nota de seguridad: no se distingue en el mensaje de error entre
"usuario no existe" y "contraseña incorrecta", para no filtrar
información útil a un atacante (enumeración de usuarios). Ambos
casos devuelven `InvalidCredentialsError`.
"""
from __future__ import annotations

from src.application.dtos.auth_dto import LoginInput, TokenOutput
from src.application.interfaces.password_hasher import PasswordHasher
from src.application.interfaces.token_service import TokenService
from src.domain.exceptions.domain_exceptions import InactiveUserError, InvalidCredentialsError
from src.domain.repositories.user_repository import UserRepository


class AuthenticateUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._repository = user_repository
        self._hasher = password_hasher
        self._tokens = token_service

    def execute(self, data: LoginInput) -> TokenOutput:
        user = self._repository.get_by_username(data.username)
        if user is None or not self._hasher.verify(data.password, user.hashed_password):
            raise InvalidCredentialsError("Usuario o contraseña incorrectos.")
        if not user.is_active:
            raise InactiveUserError("El usuario se encuentra desactivado.")

        token = self._tokens.create_access_token(
            subject=str(user.id),
            extra_claims={"username": user.username, "role": user.role.value},
        )
        return TokenOutput(access_token=token)
