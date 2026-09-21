"""Configuración de la suite de pruebas funcionales.

Todos los valores son sobreescribibles vía variables de entorno, para no
hardcodear credenciales ni URLs en el código de las pruebas.
"""
import os

# URL base del servidor corriendo. Cambia esto si la API corre en otro
# host/puerto (ej. un ambiente de staging).
BASE_URL = os.environ.get("FUNCTIONAL_TEST_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

# Credenciales del admin sembrado al arrancar la aplicación (ver .env del backend).
ADMIN_USERNAME = os.environ.get("FUNCTIONAL_TEST_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("FUNCTIONAL_TEST_ADMIN_PASSWORD", "CambiaEstaClave123!")

# Timeout de cada petición HTTP, en segundos.
REQUEST_TIMEOUT = int(os.environ.get("FUNCTIONAL_TEST_TIMEOUT", "10"))
