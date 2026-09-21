"""Dependencias de FastAPI para autenticación (JWT) y autorización (RBAC).

`get_current_user` valida el token y carga el usuario desde la base
de datos. `require_role(*roles)` es una fábrica de dependencias que
restringe el acceso a los roles indicados; cada endpoint declara
explícitamente qué rol(es) puede consumirlo.
"""
from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.domain.entities.user import User, UserRole
from src.domain.exceptions.domain_exceptions import InvalidCredentialsError
from src.infrastructure.database.connection import get_db
from src.infrastructure.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from src.infrastructure.security.jwt_token_service import JWTTokenService
from src.infrastructure.config.settings import get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_token_service() -> JWTTokenService:
    settings = get_settings()
    return JWTTokenService(
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    token_service: JWTTokenService = Depends(get_token_service),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = token_service.decode_token(token)
    except InvalidCredentialsError as exc:
        raise credentials_exception from exc

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    repository = SqlAlchemyUserRepository(db)
    user = repository.get_by_id(int(user_id))
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_role(*allowed_roles: UserRole) -> Callable[[User], User]:
    """Fábrica de dependencias: exige que el usuario actual tenga uno de los roles dados."""

    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos suficientes para realizar esta acción.",
            )
        return current_user

    return _dependency
