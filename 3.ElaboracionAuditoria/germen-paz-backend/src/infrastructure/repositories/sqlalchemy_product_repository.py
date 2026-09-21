"""Implementación concreta de ProductRepository usando SQLAlchemy.

Toda consulta usa el ORM (queries parametrizadas de forma nativa),
nunca concatenación de strings SQL, lo que elimina la superficie de
inyección SQL en esta capa.
"""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.domain.entities.product import Product
from src.domain.repositories.product_repository import ProductRepository
from src.infrastructure.database.models import ProductModel


def _to_entity(model: ProductModel) -> Product:
    return Product(
        id=model.id,
        nombre=model.nombre,
        descripcion=model.descripcion,
        precio=model.precio,
        stock=model.stock,
        categoria=model.categoria,
        activo=model.activo,
        creado_por=model.creado_por,
        fecha_creacion=model.fecha_creacion,
        fecha_actualizacion=model.fecha_actualizacion,
    )


class SqlAlchemyProductRepository(ProductRepository):
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, product: Product) -> Product:
        model = ProductModel(
            nombre=product.nombre,
            descripcion=product.descripcion,
            precio=product.precio,
            stock=product.stock,
            categoria=product.categoria,
            activo=product.activo,
            creado_por=product.creado_por,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return _to_entity(model)

    def get_by_id(self, product_id: int) -> Product | None:
        model = self._db.get(ProductModel, product_id)
        return _to_entity(model) if model else None

    def list(
        self,
        skip: int = 0,
        limit: int = 20,
        categoria: str | None = None,
        activo: bool | None = None,
        nombre: str | None = None,
    ) -> tuple[list[Product], int]:
        stmt = select(ProductModel)
        count_stmt = select(func.count()).select_from(ProductModel)

        if categoria is not None:
            stmt = stmt.where(ProductModel.categoria == categoria)
            count_stmt = count_stmt.where(ProductModel.categoria == categoria)
        if activo is not None:
            stmt = stmt.where(ProductModel.activo == activo)
            count_stmt = count_stmt.where(ProductModel.activo == activo)
        if nombre is not None:
            # like con parámetro ligado: SQLAlchemy escapa el valor automáticamente.
            stmt = stmt.where(ProductModel.nombre.ilike(f"%{nombre}%"))
            count_stmt = count_stmt.where(ProductModel.nombre.ilike(f"%{nombre}%"))

        total = self._db.scalar(count_stmt) or 0
        stmt = stmt.order_by(ProductModel.id).offset(skip).limit(limit)
        models = self._db.scalars(stmt).all()
        return [_to_entity(m) for m in models], total

    def update(self, product: Product) -> Product:
        model = self._db.get(ProductModel, product.id)
        if model is None:
            raise ValueError(f"Producto con id {product.id} no existe.")
        model.nombre = product.nombre
        model.descripcion = product.descripcion
        model.precio = product.precio
        model.stock = product.stock
        model.categoria = product.categoria
        model.activo = product.activo
        self._db.commit()
        self._db.refresh(model)
        return _to_entity(model)

    def soft_delete(self, product_id: int) -> None:
        model = self._db.get(ProductModel, product_id)
        if model is None:
            raise ValueError(f"Producto con id {product_id} no existe.")
        model.activo = False
        self._db.commit()
