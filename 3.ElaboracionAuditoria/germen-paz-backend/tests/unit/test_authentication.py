"""Pruebas unitarias de autenticación (login) y registro de usuarios."""
from __future__ import annotations

import pytest

from src.application.dtos.auth_dto import LoginInput, RegisterUserInput
from src.application.use_cases.authenticate_user import AuthenticateUserUseCase
from src.application.use_cases.register_user import RegisterUserUseCase
from src.domain.entities.user import UserRole
from src.domain.exceptions.domain_exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)


class TestAuthenticateUserUseCase:
    def test_login_exitoso_devuelve_token(self, user_repository, password_hasher, token_service, admin_user):
        use_case = AuthenticateUserUseCase(user_repository, password_hasher, token_service)

        result = use_case.execute(LoginInput(username="admin", password="AdminPass123!"))

        assert result.access_token == f"fake-token-for-{admin_user.id}"
        assert result.token_type == "bearer"

    def test_login_falla_con_password_incorrecta(self, user_repository, password_hasher, token_service, admin_user):
        use_case = AuthenticateUserUseCase(user_repository, password_hasher, token_service)

        with pytest.raises(InvalidCredentialsError):
            use_case.execute(LoginInput(username="admin", password="clave-incorrecta"))

    def test_login_falla_con_usuario_inexistente(self, user_repository, password_hasher, token_service):
        use_case = AuthenticateUserUseCase(user_repository, password_hasher, token_service)

        with pytest.raises(InvalidCredentialsError):
            use_case.execute(LoginInput(username="no-existe", password="cualquiera"))

    def test_login_falla_si_usuario_inactivo(self, user_repository, password_hasher, token_service, admin_user):
        admin_user.is_active = False
        use_case = AuthenticateUserUseCase(user_repository, password_hasher, token_service)

        with pytest.raises(InactiveUserError):
            use_case.execute(LoginInput(username="admin", password="AdminPass123!"))


class TestRegisterUserUseCase:
    def test_registra_usuario_correctamente(self, user_repository, password_hasher):
        use_case = RegisterUserUseCase(user_repository, password_hasher)

        result = use_case.execute(
            RegisterUserInput(
                username="operador2", email="operador2@germendepaz.org", password="Clave123!", role=UserRole.OPERADOR
            )
        )

        assert result.id is not None
        assert result.role == UserRole.OPERADOR

    def test_falla_si_username_ya_existe(self, user_repository, password_hasher, admin_user):
        use_case = RegisterUserUseCase(user_repository, password_hasher)

        with pytest.raises(UserAlreadyExistsError):
            use_case.execute(
                RegisterUserInput(
                    username="admin", email="otro@germendepaz.org", password="Clave123!", role=UserRole.OPERADOR
                )
            )

    def test_falla_si_email_ya_existe(self, user_repository, password_hasher, admin_user):
        use_case = RegisterUserUseCase(user_repository, password_hasher)

        with pytest.raises(UserAlreadyExistsError):
            use_case.execute(
                RegisterUserInput(
                    username="otro-usuario",
                    email="admin@germendepaz.org",
                    password="Clave123!",
                    role=UserRole.OPERADOR,
                )
            )
