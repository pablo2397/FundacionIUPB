"""Excepciones propias del dominio.

Estas excepciones no conocen HTTP ni FastAPI: son traducidas a
respuestas HTTP en la capa de presentación (core/middlewares).
"""


class DomainError(Exception):
    """Excepción base para todos los errores de dominio."""


class InvalidProductDataError(DomainError):
    """Se lanza cuando los datos de un producto violan una regla de negocio."""


class ProductNotFoundError(DomainError):
    """Se lanza cuando no se encuentra un producto solicitado."""


class UserNotFoundError(DomainError):
    """Se lanza cuando no se encuentra un usuario solicitado."""


class UserAlreadyExistsError(DomainError):
    """Se lanza al intentar registrar un usuario con username/email duplicado."""


class InvalidCredentialsError(DomainError):
    """Se lanza cuando las credenciales de login son inválidas."""


class InactiveUserError(DomainError):
    """Se lanza cuando un usuario desactivado intenta autenticarse."""


class PermissionDeniedError(DomainError):
    """Se lanza cuando un usuario no tiene el rol requerido para una operación."""
