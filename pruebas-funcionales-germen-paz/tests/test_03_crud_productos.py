"""
PASO 3 — Pruebas funcionales de CRUD de PRODUCTOS.

Cubre: creación (válida e inválida), listado (paginación y filtros),
obtención por ID (existente e inexistente), actualización completa (PUT) y
parcial (PATCH), y eliminación (DELETE, soft delete).

Prerrequisito lógico: haber verificado autenticación (paso 1) y autorización
(paso 2). Todas las operaciones de este archivo usan al admin, ya que el
paso 2 ya demostró que admin y operador comparten permisos de lectura/escritura
de productos (solo difieren en DELETE, cubierto en el paso 2).
"""
import requests

from config import BASE_URL, REQUEST_TIMEOUT


def _crear_producto(admin_headers: dict, **overrides) -> dict:
    payload = {
        "nombre": "Producto de prueba",
        "descripcion": "descripción de prueba",
        "precio": 100.0,
        "stock": 10,
        "categoria": "qa-crud",
    }
    payload.update(overrides)
    response = requests.post(f"{BASE_URL}/products", json=payload, headers=admin_headers, timeout=REQUEST_TIMEOUT)
    assert response.status_code == 201, f"Falló la creación de datos de prueba: {response.text}"
    return response.json()


class TestCrudProductosCrear:
    def test_01_crear_producto_valido(self, admin_headers: dict):
        payload = {
            "nombre": "Cuaderno ecológico QA",
            "descripcion": "Cuaderno reciclado para pruebas",
            "precio": 12500,
            "stock": 50,
            "categoria": "papeleria",
        }

        response = requests.post(f"{BASE_URL}/products", json=payload, headers=admin_headers, timeout=REQUEST_TIMEOUT)

        assert response.status_code == 201
        body = response.json()
        assert body["nombre"] == payload["nombre"]
        assert body["activo"] is True
        assert "id" in body and "fecha_creacion" in body

    def test_02_crear_producto_falla_con_precio_negativo(self, admin_headers: dict):
        payload = {"nombre": "Producto inválido", "descripcion": "", "precio": -10, "stock": 1, "categoria": "qa"}

        response = requests.post(f"{BASE_URL}/products", json=payload, headers=admin_headers, timeout=REQUEST_TIMEOUT)

        # Pydantic rechaza el precio negativo a nivel de schema (Field ge=0)
        # antes de que la petición llegue al caso de uso.
        assert response.status_code == 422

    def test_03_crear_producto_falla_con_nombre_en_blanco(self, admin_headers: dict):
        payload = {"nombre": "   ", "descripcion": "", "precio": 10, "stock": 1, "categoria": "qa"}

        response = requests.post(f"{BASE_URL}/products", json=payload, headers=admin_headers, timeout=REQUEST_TIMEOUT)

        # "   " pasa la validación de longitud mínima de Pydantic, pero la
        # regla de negocio del dominio (Product.validate()) rechaza nombres
        # en blanco -> 400, no 422. Distinguir estos dos códigos es en sí
        # mismo parte de lo que valida esta prueba.
        assert response.status_code == 400

    def test_04_crear_producto_falla_sin_campos_obligatorios(self, admin_headers: dict):
        response = requests.post(f"{BASE_URL}/products", json={"descripcion": "sin nombre ni precio"}, headers=admin_headers, timeout=REQUEST_TIMEOUT)

        assert response.status_code == 422


class TestCrudProductosListar:
    def test_05_listar_productos_con_paginacion(self, admin_headers: dict):
        for i in range(3):
            _crear_producto(admin_headers, nombre=f"Paginación QA {i}", categoria="qa-paginacion")

        response = requests.get(
            f"{BASE_URL}/products", params={"skip": 0, "limit": 2}, headers=admin_headers, timeout=REQUEST_TIMEOUT
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["items"]) == 2
        assert body["limit"] == 2
        assert body["skip"] == 0

    def test_06_listar_productos_filtrando_por_categoria(self, admin_headers: dict):
        _crear_producto(admin_headers, nombre="Filtro categoría QA", categoria="qa-filtro-unico")

        response = requests.get(
            f"{BASE_URL}/products", params={"categoria": "qa-filtro-unico"}, headers=admin_headers, timeout=REQUEST_TIMEOUT
        )

        assert response.status_code == 200
        body = response.json()
        assert body["total"] >= 1
        assert all(item["categoria"] == "qa-filtro-unico" for item in body["items"])

    def test_07_listar_productos_filtrando_por_nombre_parcial(self, admin_headers: dict):
        producto = _crear_producto(admin_headers, nombre="Termo QA Inoxidable")

        response = requests.get(
            f"{BASE_URL}/products", params={"nombre": "termo qa"}, headers=admin_headers, timeout=REQUEST_TIMEOUT
        )

        assert response.status_code == 200
        ids_encontrados = [item["id"] for item in response.json()["items"]]
        assert producto["id"] in ids_encontrados


class TestCrudProductosObtener:
    def test_08_obtener_producto_existente_por_id(self, admin_headers: dict):
        producto = _crear_producto(admin_headers, nombre="Buscar por ID QA")

        response = requests.get(f"{BASE_URL}/products/{producto['id']}", headers=admin_headers, timeout=REQUEST_TIMEOUT)

        assert response.status_code == 200
        assert response.json()["id"] == producto["id"]

    def test_09_obtener_producto_inexistente_devuelve_404(self, admin_headers: dict):
        response = requests.get(f"{BASE_URL}/products/999999999", headers=admin_headers, timeout=REQUEST_TIMEOUT)

        assert response.status_code == 404


class TestCrudProductosActualizar:
    def test_10_actualizar_producto_completo_put(self, admin_headers: dict):
        producto = _crear_producto(admin_headers, nombre="Original PUT", descripcion="desc original", precio=100, stock=5)

        update_payload = {
            "nombre": "Actualizado PUT",
            "descripcion": "desc actualizada",
            "precio": 200,
            "stock": 8,
            "categoria": "qa-actualizado",
            "activo": True,
        }
        response = requests.put(
            f"{BASE_URL}/products/{producto['id']}", json=update_payload, headers=admin_headers, timeout=REQUEST_TIMEOUT
        )

        assert response.status_code == 200
        body = response.json()
        assert body["nombre"] == "Actualizado PUT"
        assert body["precio"] == 200
        assert body["stock"] == 8

    def test_11_actualizar_producto_parcial_patch_no_toca_otros_campos(self, admin_headers: dict):
        producto = _crear_producto(admin_headers, nombre="Original PATCH", stock=5)

        response = requests.patch(
            f"{BASE_URL}/products/{producto['id']}", json={"stock": 42}, headers=admin_headers, timeout=REQUEST_TIMEOUT
        )

        assert response.status_code == 200
        body = response.json()
        assert body["stock"] == 42
        assert body["nombre"] == "Original PATCH"  # no debió modificarse

    def test_12_actualizar_producto_falla_con_stock_negativo(self, admin_headers: dict):
        producto = _crear_producto(admin_headers, nombre="Stock inválido PATCH")

        response = requests.patch(
            f"{BASE_URL}/products/{producto['id']}", json={"stock": -5}, headers=admin_headers, timeout=REQUEST_TIMEOUT
        )

        assert response.status_code == 422

    def test_13_actualizar_producto_inexistente_devuelve_404(self, admin_headers: dict):
        response = requests.patch(
            f"{BASE_URL}/products/999999999", json={"stock": 1}, headers=admin_headers, timeout=REQUEST_TIMEOUT
        )

        assert response.status_code == 404


class TestCrudProductosEliminar:
    def test_14_eliminar_producto_es_soft_delete(self, admin_headers: dict):
        producto = _crear_producto(admin_headers, nombre="Para soft delete QA")

        delete_resp = requests.delete(
            f"{BASE_URL}/products/{producto['id']}", headers=admin_headers, timeout=REQUEST_TIMEOUT
        )
        assert delete_resp.status_code == 204

        # Soft delete: el registro debe seguir existiendo, pero con activo=False.
        get_resp = requests.get(f"{BASE_URL}/products/{producto['id']}", headers=admin_headers, timeout=REQUEST_TIMEOUT)
        assert get_resp.status_code == 200
        assert get_resp.json()["activo"] is False

    def test_15_eliminar_producto_inexistente_devuelve_404(self, admin_headers: dict):
        response = requests.delete(f"{BASE_URL}/products/999999999", headers=admin_headers, timeout=REQUEST_TIMEOUT)

        assert response.status_code == 404
