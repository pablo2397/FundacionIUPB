"""Fixtures compartidos para pruebas unitarias.

Las pruebas unitarias NO tocan SQLite real: usan implementaciones
"fake" en memoria de los repositorios (mismo contrato/ABC que las
implementaciones reales), tal como exige Clean Architecture para
aislar los casos de uso de la infraestructura.
"""
from __future__ import annotations

import pytest

from src.application.interfaces.password_hasher import PasswordHasher
from src.application.interfaces.token_service import TokenService
from src.domain.entities.product import Product
from src.domain.entities.user import User, UserRole
from src.domain.repositories.product_repository import ProductRepository
from src.domain.repositories.user_repository import UserRepository


class FakeProductRepository(ProductRepository):
    def __init__(self) -> None:
        self._items: dict[int, Product] = {}
        self._next_id = 1

    def create(self, product: Product) -> Product:
        product.id = self._next_id
        self._items[self._next_id] = product
        self._next_id += 1
        return product

    def get_by_id(self, product_id: int) -> Product | None:
        return self._items.get(product_id)

    def list(
        self,
        skip: int = 0,
        limit: int = 20,
        categoria: str | None = None,
        activo: bool | None = None,
        nombre: str | None = None,
    ) -> tuple[list[Product], int]:
        values = list(self._items.values())
        if categoria is not None:
            values = [p for p in values if p.categoria == categoria]
        if activo is not None:
            values = [p for p in values if p.activo == activo]
        if nombre is not None:
            values = [p for p in values if nombre.lower() in p.nombre.lower()]
        total = len(values)
        return values[skip : skip + limit], total

    def update(self, product: Product) -> Product:
        self._items[product.id] = product  # type: ignore[index]
        return product

    def soft_delete(self, product_id: int) -> None:
        if product_id in self._items:
            self._items[product_id].activo = False


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self._items: dict[int, User] = {}
        self._next_id = 1

    def create(self, user: User) -> User:
        user.id = self._next_id
        self._items[self._next_id] = user
        self._next_id += 1
        return user

    def get_by_id(self, user_id: int) -> User | None:
        return self._items.get(user_id)

    def get_by_username(self, username: str) -> User | None:
        return next((u for u in self._items.values() if u.username == username), None)

    def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._items.values() if u.email == email), None)

    def list(self, skip: int = 0, limit: int = 20) -> tuple[list[User], int]:
        values = list(self._items.values())
        return values[skip : skip + limit], len(values)


class FakePasswordHasher(PasswordHasher):
    """Hasher fake: solo antepone un prefijo, para pruebas rápidas sin bcrypt real."""

    def hash(self, plain_password: str) -> str:
        return f"hashed::{plain_password}"

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed::{plain_password}"


class FakeTokenService(TokenService):
    def create_access_token(self, subject: str, extra_claims: dict | None = None) -> str:
        return f"fake-token-for-{subject}"

    def decode_token(self, token: str) -> dict:
        subject = token.replace("fake-token-for-", "")
        return {"sub": subject}


@pytest.fixture
def product_repository() -> FakeProductRepository:
    return FakeProductRepository()


@pytest.fixture
def user_repository() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def password_hasher() -> FakePasswordHasher:
    return FakePasswordHasher()


@pytest.fixture
def token_service() -> FakeTokenService:
    return FakeTokenService()


@pytest.fixture
def admin_user(user_repository: FakeUserRepository, password_hasher: FakePasswordHasher) -> User:
    user = User(
        id=None,
        username="admin",
        email="admin@germendepaz.org",
        hashed_password=password_hasher.hash("AdminPass123!"),
        role=UserRole.ADMIN,
    )
    return user_repository.create(user)


@pytest.fixture
def operador_user(user_repository: FakeUserRepository, password_hasher: FakePasswordHasher) -> User:
    user = User(
        id=None,
        username="operador1",
        email="operador1@germendepaz.org",
        hashed_password=password_hasher.hash("OperadorPass123!"),
        role=UserRole.OPERADOR,
    )
    return user_repository.create(user)
