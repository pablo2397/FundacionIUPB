"""Fixtures compartidos por toda la suite de pruebas funcionales.

`admin_token` y `operador_token` tienen alcance de sesión (`scope="session"`):
se calculan una sola vez por ejecución de pytest y se reutilizan en todos los
archivos de test. Esto es intencional: reduce el número de llamadas a
POST /auth/login durante la suite normal, dejando margen dentro del rate
limit (5/minuto) para la prueba dedicada de fuerza bruta que se ejecuta al
final (ver tests/test_04_rate_limiting.py).
"""
import time
import uuid

import pytest
import requests

from config import ADMIN_PASSWORD, ADMIN_USERNAME, BASE_URL, REQUEST_TIMEOUT

# Ventana del rate limit configurado en el backend (LOGIN_RATE_LIMIT=5/minute
# por defecto). Si un fixture de login recibe 429 -porque test_01 u otra
# corrida reciente ya consumió la cuota-, espera esto y reintenta UNA vez, en
# lugar de romper toda la suite. Es el comportamiento correcto para un cliente
# automatizado que consume una API con rate limiting real.
RATE_LIMIT_WAIT_SECONDS = 65


def unique_suffix() -> str:
    """Genera un sufijo aleatorio corto para evitar colisiones de username/email
    al reejecutar la suite contra una base de datos que persiste entre corridas."""
    return uuid.uuid4().hex[:8]


def _login_con_reintento(session: requests.Session, payload: dict) -> requests.Response:
    """POST /auth/login que reintenta una vez si el servidor responde 429
    (rate limit de fuerza bruta ya agotado por otras pruebas en la misma
    ventana de 1 minuto)."""
    response = session.post(f"{BASE_URL}/auth/login", json=payload, timeout=REQUEST_TIMEOUT)
    if response.status_code == 429:
        time.sleep(RATE_LIMIT_WAIT_SECONDS)
        response = session.post(f"{BASE_URL}/auth/login", json=payload, timeout=REQUEST_TIMEOUT)
    return response


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="session")
def api_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    yield session
    session.close()


@pytest.fixture(scope="session")
def admin_token(api_session: requests.Session) -> str:
    response = _login_con_reintento(
        api_session, {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200, (
        "No fue posible autenticar al admin para preparar las pruebas. "
        f"¿Está el servidor corriendo en {BASE_URL}? Respuesta: "
        f"{response.status_code} {response.text}"
    )
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def admin_headers(admin_token: str) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="session")
def operador_credentials(api_session: requests.Session, admin_headers: dict) -> dict:
    """Crea, vía el admin, un usuario con rol operador único para toda la sesión de pruebas."""
    suffix = unique_suffix()
    username = f"qa_operador_{suffix}"
    password = "OperadorQA123!"

    response = api_session.post(
        f"{BASE_URL}/auth/register",
        json={
            "username": username,
            "email": f"{username}@germendepaz.org",
            "password": password,
            "role": "operador",
        },
        headers=admin_headers,
        timeout=REQUEST_TIMEOUT,
    )
    assert response.status_code == 201, f"No fue posible crear el operador de pruebas: {response.text}"
    return {"username": username, "password": password}


@pytest.fixture(scope="session")
def operador_token(api_session: requests.Session, operador_credentials: dict) -> str:
    response = _login_con_reintento(api_session, operador_credentials)
    assert response.status_code == 200, f"No fue posible autenticar al operador de pruebas: {response.text}"
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def operador_headers(operador_token: str) -> dict:
    return {"Authorization": f"Bearer {operador_token}"}
