"""
PASO 2 — Pruebas funcionales de AUTORIZACIÓN (RBAC).

Verifica que cada endpoint respeta los roles declarados en el código:
- admin: CRUD completo de productos + gestión de usuarios (registro)
- operador: lectura y creación de productos, SIN eliminar ni registrar usuarios

Prerrequisito lógico: haber verificado primero que la autenticación funciona
(paso 1). Usa las fixtures de sesión `admin_headers` y `operador_headers`
definidas en conftest.py (login hecho una sola vez para toda la suite).
"""
import requests

from config import BASE_URL, REQUEST_TIMEOUT
from conftest import unique_suffix


class TestAutorizacionRBAC:
    def test_01_admin_puede_registrar_un_nuevo_usuario(self, admin_headers: dict):
        suffix = unique_suffix()
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": f"qa_check_{suffix}",
                "email": f"qa_check_{suffix}@germendepaz.org",
                "password": "Clave123456!",
                "role": "operador",
            },
            headers=admin_headers,
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 201
        assert response.json()["role"] == "operador"

    def test_02_operador_no_puede_registrar_usuarios(self, operador_headers: dict):
        suffix = unique_suffix()
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": f"qa_no_autorizado_{suffix}",
                "email": f"qa_no_autorizado_{suffix}@germendepaz.org",
                "password": "Clave123456!",
                "role": "operador",
            },
            headers=operador_headers,
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 403

    def test_03_admin_y_operador_pueden_crear_productos(self, admin_headers: dict, operador_headers: dict):
        payload_base = {
            "descripcion": "creado en prueba de autorización",
            "precio": 1000,
            "stock": 5,
            "categoria": "qa-rbac",
        }

        resp_admin = requests.post(
            f"{BASE_URL}/products",
            json={**payload_base, "nombre": "Producto RBAC (admin)"},
            headers=admin_headers,
            timeout=REQUEST_TIMEOUT,
        )
        resp_operador = requests.post(
            f"{BASE_URL}/products",
            json={**payload_base, "nombre": "Producto RBAC (operador)"},
            headers=operador_headers,
            timeout=REQUEST_TIMEOUT,
        )

        assert resp_admin.status_code == 201
        assert resp_operador.status_code == 201

    def test_04_admin_y_operador_pueden_listar_y_leer_productos(self, admin_headers: dict, operador_headers: dict):
        for headers in (admin_headers, operador_headers):
            response = requests.get(f"{BASE_URL}/products", headers=headers, timeout=REQUEST_TIMEOUT)
            assert response.status_code == 200

    def test_05_operador_no_puede_eliminar_productos(self, admin_headers: dict, operador_headers: dict):
        create_resp = requests.post(
            f"{BASE_URL}/products",
            json={"nombre": "Para eliminar (RBAC)", "descripcion": "", "precio": 100, "stock": 1, "categoria": "qa-rbac"},
            headers=admin_headers,
            timeout=REQUEST_TIMEOUT,
        )
        product_id = create_resp.json()["id"]

        response = requests.delete(
            f"{BASE_URL}/products/{product_id}", headers=operador_headers, timeout=REQUEST_TIMEOUT
        )

        assert response.status_code == 403

    def test_06_admin_si_puede_eliminar_productos(self, admin_headers: dict):
        create_resp = requests.post(
            f"{BASE_URL}/products",
            json={"nombre": "Para eliminar admin (RBAC)", "descripcion": "", "precio": 100, "stock": 1, "categoria": "qa-rbac"},
            headers=admin_headers,
            timeout=REQUEST_TIMEOUT,
        )
        product_id = create_resp.json()["id"]

        response = requests.delete(
            f"{BASE_URL}/products/{product_id}", headers=admin_headers, timeout=REQUEST_TIMEOUT
        )

        assert response.status_code == 204
