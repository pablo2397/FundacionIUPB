"""Configuración de logging para eventos de autenticación y operaciones críticas.

Nunca se registran contraseñas ni tokens completos en los logs.
"""
from __future__ import annotations

import logging
import sys


def setup_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )
    # Evita que librerías de terceros inunden el log en modo debug.
    logging.getLogger("passlib").setLevel(logging.WARNING)


security_logger = logging.getLogger("germen_paz.security")
