"""
Administrador de workers: lanza workers de generación y edición en paralelo.
Usa concurrent.futures (ThreadPoolExecutor) para simular múltiples IAs generando libros.
"""
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from config.settings import (
    WORKERS_GENERATE,
    WORKERS_EDIT,
    MAX_CONCURRENT_BOOKS,
    GENERATION_INTERVAL_SECONDS,
)

logger = logging.getLogger(__name__)


def run_worker_pool(
    workers_generate: int = WORKERS_GENERATE,
    workers_edit: int = WORKERS_EDIT,
    interval_seconds: int = GENERATION_INTERVAL_SECONDS,
    max_concurrent: int = MAX_CONCURRENT_BOOKS,
) -> None:
    """
    Bucle infinito: lanza generaciones cada interval_seconds,
    con hasta workers_generate workers de generación en paralelo (threads).
    Un solo proceso = una sola carga del modelo.
    """
    logger.info(
        "Iniciando pool: generate=%s, edit=%s, intervalo=%ss, max_concurrent=%s",
        workers_generate, workers_edit, interval_seconds, max_concurrent,
    )

    from workers.worker_generate import run_generate_worker

    while True:
        try:
            n = min(workers_generate, max_concurrent)
            with ThreadPoolExecutor(max_workers=n) as executor:
                futures = [executor.submit(run_generate_worker, "Ficción") for _ in range(n)]
                for fut in as_completed(futures):
                    try:
                        result = fut.result()
                        if result:
                            logger.info("Libro generado: id=%s", result.get("id"))
                    except Exception as e:
                        logger.exception("Worker falló: %s", e)
        except Exception as e:
            logger.exception("Error en pool de generación: %s", e)

        logger.info("Esperando %s segundos hasta la siguiente ronda...", interval_seconds)
        time.sleep(interval_seconds)


def run_single_cycle() -> None:
    """Ejecuta una sola ronda de generación (útil para pruebas)."""
    from workers.worker_generate import run_generate_worker
    run_generate_worker("Ficción")
