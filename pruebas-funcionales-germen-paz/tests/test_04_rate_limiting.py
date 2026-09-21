"""
PASO 4 — Prueba funcional de RATE LIMITING (mitigación de fuerza bruta en login).

¿Por qué es el ÚLTIMO archivo de la suite y no parte del paso 1?
-----------------------------------------------------------------
El límite configurado es de 5 peticiones/minuto por IP sobre POST /auth/login
(ver slowapi en el backend). Esta prueba agota ese límite a propósito para
verificar que el servidor responde 429 tras varios intentos fallidos. Si esta
prueba corriera primero, dejaría el límite "consumido" durante ~1 minuto y
haría fallar por 429 (no por un error real) los logins que necesitan los
pasos 2 y 3 para preparar sus datos. Por eso se ejecuta al final.

Nota: si vuelves a correr la suite completa inmediatamente después de este
archivo, espera aproximadamente 60 segundos para que la ventana del rate
limit se libere.
"""
import requests

from config import BASE_URL, REQUEST_TIMEOUT


class TestRateLimitingLogin:
    def test_01_login_bloquea_tras_multiples_intentos_fallidos(self):
        max_intentos = 15
        codigos_obtenidos = []

        for _ in range(max_intentos):
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": "admin", "password": "clave-incorrecta-fuerza-bruta"},
                timeout=REQUEST_TIMEOUT,
            )
            codigos_obtenidos.append(response.status_code)
            if response.status_code == 429:
                break

        assert 429 in codigos_obtenidos, (
            "Se esperaba que el rate limiting bloqueara el login tras varios "
            f"intentos fallidos, pero no se recibió 429 en {max_intentos} intentos. "
            f"Códigos obtenidos: {codigos_obtenidos}"
        )
