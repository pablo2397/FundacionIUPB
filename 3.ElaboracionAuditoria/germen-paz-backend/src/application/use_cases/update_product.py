"""Caso de uso: actualizar un producto (soporta actualización parcial)."""
from __future__ import annotations

from src.application.dtos.product_dto import ProductOutput, UpdateProductInput
from src.domain.exceptions.domain_exceptions import ProductNotFoundError
from src.domain.repositories.product_repository import ProductRepository


class UpdateProductUseCase:
    def __init__(self, product_repository: ProductRepository) -> None:
        self._repository = product_repository

    def execute(self, product_id: int, data: UpdateProductInput) -> ProductOutput:
        product = self._repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(f"Producto con id {product_id} no encontrado.")

        if data.nombre is not None:
            product.nombre = data.nombre
        if data.descripcion is not None:
            product.descripcion = data.descripcion
        if data.precio is not None:
            product.precio = data.precio
        if data.stock is not None:
            product.actualizar_stock(data.stock)
        if data.categoria is not None:
            product.categoria = data.categoria
        if data.activo is not None:
            product.activo = data.activo

        # Re-valida invariantes de negocio tras aplicar los cambios.
        product.validate()

        updated = self._repository.update(product)
        return ProductOutput(
            id=updated.id,  # type: ignore[arg-type]
            nombre=updated.nombre,
            descripcion=updated.descripcion,
            precio=updated.precio,
            stock=updated.stock,
            categoria=updated.categoria,
            activo=updated.activo,
            creado_por=updated.creado_por,
            fecha_creacion=updated.fecha_creacion,
            fecha_actualizacion=updated.fecha_actualizacion,
        )
