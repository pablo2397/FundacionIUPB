"""Fábricas (providers) que ensamblan casos de uso con sus dependencias
concretas de infraestructura, para inyectarlos en los routers vía
`Depends(...)`. Este es el único lugar donde `core` conoce
implementaciones concretas de `infrastructure`; el resto de la
aplicación (domain, application) permanece desacoplado.
"""
from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from src.application.use_cases.authenticate_user import AuthenticateUserUseCase
from src.application.use_cases.create_product import CreateProductUseCase
from src.application.use_cases.delete_product import DeleteProductUseCase
from src.application.use_cases.get_product import GetProductUseCase
from src.application.use_cases.list_products import ListProductsUseCase
from src.application.use_cases.register_user import RegisterUserUseCase
from src.application.use_cases.update_product import UpdateProductUseCase
from src.core.dependencies.auth import get_token_service
from src.infrastructure.database.connection import get_db
from src.infrastructure.repositories.sqlalchemy_product_repository import (
    SqlAlchemyProductRepository,
)
from src.infrastructure.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from src.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from src.infrastructure.security.jwt_token_service import JWTTokenService


def get_create_product_use_case(db: Session = Depends(get_db)) -> CreateProductUseCase:
    return CreateProductUseCase(SqlAlchemyProductRepository(db))


def get_list_products_use_case(db: Session = Depends(get_db)) -> ListProductsUseCase:
    return ListProductsUseCase(SqlAlchemyProductRepository(db))


def get_get_product_use_case(db: Session = Depends(get_db)) -> GetProductUseCase:
    return GetProductUseCase(SqlAlchemyProductRepository(db))


def get_update_product_use_case(db: Session = Depends(get_db)) -> UpdateProductUseCase:
    return UpdateProductUseCase(SqlAlchemyProductRepository(db))


def get_delete_product_use_case(db: Session = Depends(get_db)) -> DeleteProductUseCase:
    return DeleteProductUseCase(SqlAlchemyProductRepository(db))


def get_register_user_use_case(db: Session = Depends(get_db)) -> RegisterUserUseCase:
    return RegisterUserUseCase(SqlAlchemyUserRepository(db), BcryptPasswordHasher())


def get_authenticate_user_use_case(
    db: Session = Depends(get_db),
    token_service: JWTTokenService = Depends(get_token_service),
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(
        SqlAlchemyUserRepository(db), BcryptPasswordHasher(), token_service
    )
