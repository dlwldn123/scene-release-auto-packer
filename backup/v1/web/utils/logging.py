"""
Utilitaires de logging standardisés pour l'application.
"""

import logging
from functools import wraps
from typing import Optional

logger = logging.getLogger(__name__)


# Mapping exception types → log levels
EXCEPTION_LOG_LEVELS = {
    # Erreurs critiques
    ValueError: logging.ERROR,
    TypeError: logging.ERROR,
    AttributeError: logging.ERROR,
    KeyError: logging.ERROR,
    # Erreurs I/O
    FileNotFoundError: logging.WARNING,
    PermissionError: logging.WARNING,
    IOError: logging.WARNING,
    OSError: logging.WARNING,
    # Erreurs réseau
    ConnectionError: logging.WARNING,
    TimeoutError: logging.WARNING,
    # Erreurs génériques
    Exception: logging.ERROR,
}


def get_log_level_for_exception(exception: Exception) -> int:
    """
    Retourne le niveau de log approprié pour une exception.

    Args:
        exception: Exception à logger

    Returns:
        Niveau de log (logging.DEBUG, INFO, WARNING, ERROR)
    """
    exception_type = type(exception)

    # Chercher dans la hiérarchie des classes
    for exc_class, log_level in EXCEPTION_LOG_LEVELS.items():
        if issubclass(exception_type, exc_class):
            return log_level

    # Par défaut: ERROR
    return logging.ERROR


def log_exception(
    exception: Exception,
    context: Optional[str] = None,
    extra_info: Optional[dict] = None,
    logger_instance: Optional[logging.Logger] = None,
) -> None:
    """
    Log une exception avec niveau approprié et contexte.

    Args:
        exception: Exception à logger
        context: Contexte où l'erreur s'est produite (ex: "packaging ebook")
        extra_info: Informations supplémentaires à logger
        logger_instance: Logger à utiliser (None = logger par défaut)
    """
    log = logger_instance or logger
    log_level = get_log_level_for_exception(exception)

    message_parts = []
    if context:
        message_parts.append(f"[{context}]")
    message_parts.append(f"Erreur: {str(exception)}")

    message = " ".join(message_parts)

    # Logger avec niveau approprié
    if log_level == logging.ERROR:
        log.error(message, exc_info=True, extra=extra_info)
    elif log_level == logging.WARNING:
        log.warning(message, exc_info=True, extra=extra_info)
    else:
        log.log(log_level, message, exc_info=True, extra=extra_info)


def log_and_handle_exception(
    context: Optional[str] = None,
    reraise: bool = True,
    default_return=None,
):
    """
    Décorateur pour logger automatiquement les exceptions.

    Args:
        context: Contexte pour le log
        reraise: Si True, relève l'exception après logging
        default_return: Valeur à retourner si reraise=False

    Usage:
        @log_and_handle_exception(context="packaging")
        def my_function():
            ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_exception(e, context=context or func.__name__)
                if reraise:
                    raise
                return default_return

        return wrapper

    return decorator


def standardize_log_format(
    logger_name: str, format_string: Optional[str] = None
) -> logging.Logger:
    """
    Crée ou configure un logger avec format standardisé.

    Args:
        logger_name: Nom du logger
        format_string: Format personnalisé (None = format par défaut)

    Returns:
        Logger configuré
    """
    log = logging.getLogger(logger_name)

    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s"

    handler = logging.StreamHandler()
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)

    if not log.handlers:
        log.addHandler(handler)

    return log
