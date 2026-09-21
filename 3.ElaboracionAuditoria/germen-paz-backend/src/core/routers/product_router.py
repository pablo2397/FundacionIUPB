"""Endpoints CRUD del recurso Producto.

Cada endpoint declara explícitamente los roles permitidos mediante
`Depends(require_role(...))`:
- Lectura (GET): admin y operador.
- Creación (POST) y actualización (PUT/PATCH): admin y operador.
- Eliminación (DELETE): solo admin.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.application.dtos.product_dto import CreateProductInput, UpdateProductInput
from src.application.use_cases.create_product import CreateProductUseCase
from src.application.use_cases.delete_product import DeleteProductUseCase
from src.application.use_cases.get_product import GetProductUseCase
from src.application.use_cases.list_products import ListProductsUseCase
from src.application.use_cases.update_product import UpdateProductUseCase
from src.core.dependencies.auth import require_role
from src.core.dependencies.providers import (
    get_create_product_use_case,
    get_delete_product_use_case,
    get_get_product_use_case,
    get_list_products_use_case,
    get_update_product_use_case,
)
from src.core.schemas.auth_schemas import ErrorResponse
from src.core.schemas.product_schemas import (
    ProductCreateRequest,
    ProductListResponse,
    ProductPatchRequest,
    ProductResponse,
    ProductUpdateRequest,
)
from src.domain.entities.user import User, UserRole
from src.domain.exceptions.domain_exceptions import InvalidProductDataError, ProductNotFoundError

router = APIRouter(prefix="/products", tags=["Productos"])

_READ_ROLES = (UserRole.ADMIN, UserRole.OPERADOR)
_WRITE_ROLES = (UserRole.ADMIN, UserRole.OPERADOR)
_DELETE_ROLES = (UserRole.ADMIN,)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un producto",
    responses={400: {"model": ErrorResponse, "description": "Datos inválidos"}},
)
def create_product(
    payload: ProductCreateRequest,
    current_user: User = Depends(require_role(*_WRITE_ROLES)),
    use_case: CreateProductUseCase = Depends(get_create_product_use_case),
) -> ProductResponse:
    try:
        result = use_case.execute(
            CreateProductInput(
                nombre=payload.nombre,
                descripcion=payload.descripcion,
                precio=payload.precio,
                stock=payload.stock,
                categoria=payload.categoria,
                creado_por=current_user.id,  # type: ignore[arg-type]
            )
        )
    except InvalidProductDataError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ProductResponse.model_validate(result)


@router.get(
    "",
    response_model=ProductListResponse,
    summary="Listar productos (con paginación y filtros)",
)
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    categoria: str | None = Query(None),
    activo: bool | None = Query(None),
    nombre: str | None = Query(None, description="Búsqueda parcial por nombre"),
    _current_user: User = Depends(require_role(*_READ_ROLES)),
    use_case: ListProductsUseCase = Depends(get_list_products_use_case),
) -> ProductListResponse:
    result = use_case.execute(skip=skip, limit=limit, categoria=categoria, activo=activo, nombre=nombre)
    return ProductListResponse(
        items=[ProductResponse.model_validate(item) for item in result.items],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Obtener un producto por ID",
    responses={404: {"model": ErrorResponse, "description": "Producto no encontrado"}},
)
def get_product(
    product_id: int,
    _current_user: User = Depends(require_role(*_READ_ROLES)),
    use_case: GetProductUseCase = Depends(get_get_product_use_case),
) -> ProductResponse:
    try:
        result = use_case.execute(product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ProductResponse.model_validate(result)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Actualizar un producto (reemplazo completo)",
    responses={
        404: {"model": ErrorResponse, "description": "Producto no encontrado"},
        400: {"model": ErrorResponse, "description": "Datos inválidos"},
    },
)
def update_product(
    product_id: int,
    payload: ProductUpdateRequest,
    _current_user: User = Depends(require_role(*_WRITE_ROLES)),
    use_case: UpdateProductUseCase = Depends(get_update_product_use_case),
) -> ProductResponse:
    try:
        result = use_case.execute(product_id, UpdateProductInput(**payload.model_dump()))
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidProductDataError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ProductResponse.model_validate(result)


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Actualizar un producto (parcial)",
    responses={
        404: {"model": ErrorResponse, "description": "Producto no encontrado"},
        400: {"model": ErrorResponse, "description": "Datos inválidos"},
    },
)
def patch_product(
    product_id: int,
    payload: ProductPatchRequest,
    _current_user: User = Depends(require_role(*_WRITE_ROLES)),
    use_case: UpdateProductUseCase = Depends(get_update_product_use_case),
) -> ProductResponse:
    try:
        data = payload.model_dump(exclude_unset=True)
        result = use_case.execute(product_id, UpdateProductInput(**data))
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidProductDataError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ProductResponse.model_validate(result)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Eliminar un producto (soft delete, solo admin)",
    responses={
        404: {"model": ErrorResponse, "description": "Producto no encontrado"},
        403: {"model": ErrorResponse, "description": "No autorizado (rol insuficiente)"},
    },
)
def delete_product(
    product_id: int,
    _current_user: User = Depends(require_role(*_DELETE_ROLES)),
    use_case: DeleteProductUseCase = Depends(get_delete_product_use_case),
) -> None:
    try:
        use_case.execute(product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
