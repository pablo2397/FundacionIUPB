"""Caso de uso: crear un producto."""
from __future__ import annotations

from src.application.dtos.product_dto import CreateProductInput, ProductOutput
from src.domain.entities.product import Product
from src.domain.repositories.product_repository import ProductRepository


class CreateProductUseCase:
    def __init__(self, product_repository: ProductRepository) -> None:
        self._repository = product_repository

    def execute(self, data: CreateProductInput) -> ProductOutput:
        # La validación de reglas de negocio ocurre dentro de la entidad
        # (Product.__post_init__ -> validate()).
        product = Product(
            id=None,
            nombre=data.nombre,
            descripcion=data.descripcion,
            precio=data.precio,
            stock=data.stock,
            categoria=data.categoria,
            activo=True,
            creado_por=data.creado_por,
        )
        created = self._repository.create(product)
        return ProductOutput(
            id=created.id,  # type: ignore[arg-type]
            nombre=created.nombre,
            descripcion=created.descripcion,
            precio=created.precio,
            stock=created.stock,
            categoria=created.categoria,
            activo=created.activo,
            creado_por=created.creado_por,
            fecha_creacion=created.fecha_creacion,
            fecha_actualizacion=created.fecha_actualizacion,
        )
