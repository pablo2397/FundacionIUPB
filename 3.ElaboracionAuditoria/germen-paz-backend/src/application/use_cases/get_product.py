"""Caso de uso: obtener un producto por su ID."""
from __future__ import annotations

from src.application.dtos.product_dto import ProductOutput
from src.domain.exceptions.domain_exceptions import ProductNotFoundError
from src.domain.repositories.product_repository import ProductRepository


class GetProductUseCase:
    def __init__(self, product_repository: ProductRepository) -> None:
        self._repository = product_repository

    def execute(self, product_id: int) -> ProductOutput:
        product = self._repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(f"Producto con id {product_id} no encontrado.")
        return ProductOutput(
            id=product.id,  # type: ignore[arg-type]
            nombre=product.nombre,
            descripcion=product.descripcion,
            precio=product.precio,
            stock=product.stock,
            categoria=product.categoria,
            activo=product.activo,
            creado_por=product.creado_por,
            fecha_creacion=product.fecha_creacion,
            fecha_actualizacion=product.fecha_actualizacion,
        )
