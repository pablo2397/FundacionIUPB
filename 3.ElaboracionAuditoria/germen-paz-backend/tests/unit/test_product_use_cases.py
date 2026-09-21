"""Pruebas unitarias de los casos de uso de productos.

Usan `FakeProductRepository` (in-memory); no tocan SQLite real.
"""
from __future__ import annotations

import pytest

from src.application.dtos.product_dto import CreateProductInput, UpdateProductInput
from src.application.use_cases.create_product import CreateProductUseCase
from src.application.use_cases.delete_product import DeleteProductUseCase
from src.application.use_cases.get_product import GetProductUseCase
from src.application.use_cases.list_products import ListProductsUseCase
from src.application.use_cases.update_product import UpdateProductUseCase
from src.domain.exceptions.domain_exceptions import InvalidProductDataError, ProductNotFoundError


def _create_sample_product(product_repository, nombre="Cuaderno", precio=1000.0, stock=10, categoria="papeleria"):
    use_case = CreateProductUseCase(product_repository)
    return use_case.execute(
        CreateProductInput(
            nombre=nombre, descripcion="desc", precio=precio, stock=stock, categoria=categoria, creado_por=1
        )
    )


class TestCreateProductUseCase:
    def test_crea_producto_correctamente(self, product_repository):
        result = _create_sample_product(product_repository)

        assert result.id == 1
        assert result.nombre == "Cuaderno"
        assert result.activo is True

    def test_falla_con_precio_negativo(self, product_repository):
        use_case = CreateProductUseCase(product_repository)
        with pytest.raises(InvalidProductDataError):
            use_case.execute(
                CreateProductInput(
                    nombre="Producto", descripcion="", precio=-5, stock=1, categoria="x", creado_por=1
                )
            )

    def test_falla_con_nombre_vacio(self, product_repository):
        use_case = CreateProductUseCase(product_repository)
        with pytest.raises(InvalidProductDataError):
            use_case.execute(
                CreateProductInput(nombre="   ", descripcion="", precio=10, stock=1, categoria="x", creado_por=1)
            )


class TestListProductsUseCase:
    def test_lista_con_paginacion(self, product_repository):
        for i in range(5):
            _create_sample_product(product_repository, nombre=f"Producto {i}")

        use_case = ListProductsUseCase(product_repository)
        result = use_case.execute(skip=0, limit=2)

        assert result.total == 5
        assert len(result.items) == 2

    def test_filtra_por_categoria(self, product_repository):
        _create_sample_product(product_repository, nombre="A", categoria="ropa")
        _create_sample_product(product_repository, nombre="B", categoria="papeleria")

        use_case = ListProductsUseCase(product_repository)
        result = use_case.execute(categoria="ropa")

        assert result.total == 1
        assert result.items[0].categoria == "ropa"


class TestGetProductUseCase:
    def test_obtiene_producto_existente(self, product_repository):
        created = _create_sample_product(product_repository)
        use_case = GetProductUseCase(product_repository)

        result = use_case.execute(created.id)

        assert result.id == created.id

    def test_lanza_error_si_no_existe(self, product_repository):
        use_case = GetProductUseCase(product_repository)
        with pytest.raises(ProductNotFoundError):
            use_case.execute(999)


class TestUpdateProductUseCase:
    def test_actualiza_campos_parciales(self, product_repository):
        created = _create_sample_product(product_repository)
        use_case = UpdateProductUseCase(product_repository)

        result = use_case.execute(created.id, UpdateProductInput(precio=2500.0))

        assert result.precio == 2500.0
        assert result.nombre == created.nombre  # no se modificó

    def test_lanza_error_si_no_existe(self, product_repository):
        use_case = UpdateProductUseCase(product_repository)
        with pytest.raises(ProductNotFoundError):
            use_case.execute(999, UpdateProductInput(precio=10.0))

    def test_falla_con_stock_negativo(self, product_repository):
        created = _create_sample_product(product_repository)
        use_case = UpdateProductUseCase(product_repository)
        with pytest.raises(InvalidProductDataError):
            use_case.execute(created.id, UpdateProductInput(stock=-1))


class TestDeleteProductUseCase:
    def test_soft_delete_marca_inactivo(self, product_repository):
        created = _create_sample_product(product_repository)
        use_case = DeleteProductUseCase(product_repository)

        use_case.execute(created.id)

        stored = product_repository.get_by_id(created.id)
        assert stored.activo is False
        # Soft delete: el registro sigue existiendo en el repositorio.
        assert stored is not None

    def test_lanza_error_si_no_existe(self, product_repository):
        use_case = DeleteProductUseCase(product_repository)
        with pytest.raises(ProductNotFoundError):
            use_case.execute(999)
