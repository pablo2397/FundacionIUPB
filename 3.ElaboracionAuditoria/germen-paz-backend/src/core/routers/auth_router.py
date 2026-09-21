"""Endpoints de autenticación: login y registro de usuarios.

El registro (`POST /auth/register`) solo es accesible para usuarios
con rol `admin`; el usuario admin inicial se crea vía seed al
arrancar la aplicación (ver `main.py`).

Nota técnica: este módulo NO usa `from __future__ import annotations`
a propósito. El decorador `@limiter.limit(...)` de slowapi envuelve el
endpoint con `functools.wraps`, y con anotaciones "postponed" (string)
FastAPI intenta resolver los tipos usando el namespace global de la
función envuelta, que en ese caso apunta al módulo de slowapi (no al
de este router), rompiendo la resolución de `LoginRequest`. Al evaluar
las anotaciones de forma inmediata (comportamiento por defecto en
Python 3.11+ para `X | None`) se evita el problema.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.application.dtos.auth_dto import LoginInput, RegisterUserInput
from src.application.use_cases.authenticate_user import AuthenticateUserUseCase
from src.application.use_cases.register_user import RegisterUserUseCase
from src.core.dependencies.auth import require_role
from src.core.dependencies.providers import (
    get_authenticate_user_use_case,
    get_register_user_use_case,
)
from src.core.schemas.auth_schemas import (
    ErrorResponse,
    LoginRequest,
    TokenResponse,
    UserRegisterRequest,
    UserResponse,
)
from src.domain.entities.user import User, UserRole
from src.domain.exceptions.domain_exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from src.infrastructure.security.rate_limiter import limiter
from src.core.middlewares.logging_config import security_logger

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión y obtener un access token JWT",
    responses={401: {"model": ErrorResponse, "description": "Credenciales inválidas"}},
)
@limiter.limit("5/minute")  # Mitigación básica de fuerza bruta.
def login(
    request: Request,
    credentials: LoginRequest,
    use_case: AuthenticateUserUseCase = Depends(get_authenticate_user_use_case),
) -> TokenResponse:
    try:
        result = use_case.execute(LoginInput(username=credentials.username, password=credentials.password))
    except (InvalidCredentialsError, InactiveUserError) as exc:
        # Se registra el intento fallido (sin loguear la contraseña) para auditoría.
        security_logger.warning("Login fallido para username='%s'", credentials.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    security_logger.info("Login exitoso para username='%s'", credentials.username)
    return TokenResponse(access_token=result.access_token, token_type=result.token_type)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario (solo admin)",
    responses={
        403: {"model": ErrorResponse, "description": "No autorizado (rol insuficiente)"},
        409: {"model": ErrorResponse, "description": "Usuario o email ya registrado"},
    },
)
def register(
    payload: UserRegisterRequest,
    _current_admin: User = Depends(require_role(UserRole.ADMIN)),
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
) -> UserResponse:
    try:
        result = use_case.execute(
            RegisterUserInput(
                username=payload.username,
                email=payload.email,
                password=payload.password,
                role=payload.role,
            )
        )
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return UserResponse(
        id=result.id, username=result.username, email=result.email, role=result.role, is_active=result.is_active
    )
