"""
PASO 1 — Pruebas funcionales de AUTENTICACIÓN.

Cubre: POST /auth/login (login exitoso, credenciales inválidas, mensaje de
error uniforme para no filtrar existencia de usuarios) y el rechazo de
peticiones a endpoints protegidos sin token o con token inválido.

Prerrequisito: el servidor debe estar corriendo (uvicorn src.core.main:app)
y el usuario admin debe existir (se siembra automáticamente al arrancar).
Este archivo NO depende de otros pasos: se ejecuta primero por diseño.
"""
import requests

from config import ADMIN_PASSWORD, ADMIN_USERNAME, BASE_URL, REQUEST_TIMEOUT


class TestAutenticacion:
    def test_01_login_exitoso_con_credenciales_validas(self):
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body and body["access_token"]
        assert body["token_type"] == "bearer"

    def test_02_login_falla_con_password_incorrecta(self):
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": ADMIN_USERNAME, "password": "password-incorrecta"},
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 401
        assert "access_token" not in response.json()

    def test_03_login_falla_con_usuario_inexistente(self):
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "usuario_que_no_existe_qa", "password": "cualquiera"},
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 401

    def test_04_mensaje_de_error_no_distingue_usuario_inexistente_de_password_incorrecta(self):
        """Control de seguridad: el mensaje debe ser idéntico en ambos casos,
        para no permitir enumeración de usuarios a través del error devuelto."""
        resp_password_incorrecta = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": ADMIN_USERNAME, "password": "incorrecta"},
            timeout=REQUEST_TIMEOUT,
        )
        resp_usuario_inexistente = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "no_existe_qa_xyz", "password": "incorrecta"},
            timeout=REQUEST_TIMEOUT,
        )

        assert resp_password_incorrecta.status_code == 401
        assert resp_usuario_inexistente.status_code == 401
        assert resp_password_incorrecta.json()["detail"] == resp_usuario_inexistente.json()["detail"]

    def test_05_endpoint_protegido_rechaza_peticion_sin_token(self):
        response = requests.get(f"{BASE_URL}/products", timeout=REQUEST_TIMEOUT)

        assert response.status_code == 401

    def test_06_endpoint_protegido_rechaza_token_invalido_o_manipulado(self):
        headers = {"Authorization": "Bearer token.invalido.manipulado"}
        response = requests.get(f"{BASE_URL}/products", headers=headers, timeout=REQUEST_TIMEOUT)

        assert response.status_code == 401

    def test_07_login_rechaza_payload_malformado(self):
        """Validación de entrada: falta el campo 'password' -> error 422 de Pydantic."""
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": ADMIN_USERNAME},
            timeout=REQUEST_TIMEOUT,
        )

        assert response.status_code == 422
