"""Implementación concreta de UserRepository usando SQLAlchemy."""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.domain.entities.user import User, UserRole
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models import UserModel


def _to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        username=model.username,
        email=model.email,
        hashed_password=model.hashed_password,
        role=UserRole(model.role),
        is_active=model.is_active,
        created_at=model.created_at,
    )


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, user: User) -> User:
        model = UserModel(
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role.value,
            is_active=user.is_active,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return _to_entity(model)

    def get_by_id(self, user_id: int) -> User | None:
        model = self._db.get(UserModel, user_id)
        return _to_entity(model) if model else None

    def get_by_username(self, username: str) -> User | None:
        stmt = select(UserModel).where(UserModel.username == username)
        model = self._db.scalars(stmt).first()
        return _to_entity(model) if model else None

    def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        model = self._db.scalars(stmt).first()
        return _to_entity(model) if model else None

    def list(self, skip: int = 0, limit: int = 20) -> tuple[list[User], int]:
        total = self._db.scalar(select(func.count()).select_from(UserModel)) or 0
        stmt = select(UserModel).order_by(UserModel.id).offset(skip).limit(limit)
        models = self._db.scalars(stmt).all()
        return [_to_entity(m) for m in models], total
