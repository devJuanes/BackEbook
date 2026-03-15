"""
Worker de generación: ejecuta el pipeline completo (generar libro y guardar en Firebase).
"""
import logging
from typing import Any

from core.pipeline import run_pipeline

logger = logging.getLogger(__name__)


def run_generate_worker(genre: str = "Ficción") -> dict[str, Any] | None:
    """
    Ejecuta un ciclo completo de generación: analizar, generar, editar, guardar en Firebase.
    Los libros quedan en APP/eBooks para que ebook-app los muestre.
    """
    try:
        result = run_pipeline(genre=genre)
        if result:
            logger.info("Worker generación OK: libro id=%s", result.get("id"))
        return result
    except Exception as e:
        logger.exception("Worker generación falló: %s", e)
        return None
