"""
Punto de entrada de BackEbook: fábrica de generación de libros 24/7.
Conectado al mismo Firebase que ebook-app (Realtime Database APP/eBooks).
"""
import argparse
import sys

# Asegurar que el directorio raíz del proyecto esté en el path
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))

from core.log_config import setup_logging

setup_logging()

import logging
from workers.worker_manager import run_worker_pool, run_single_cycle

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="BackEbook - Fábrica de generación de libros")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Ejecutar una sola generación (pruebas). Por defecto: bucle continuo.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Segundos entre rondas de generación (solo en modo continuo).",
    )
    args = parser.parse_args()

    if args.once:
        logger.info("Modo una sola ejecución.")
        run_single_cycle()
        return

    interval = args.interval if args.interval is not None else None
    from config.settings import GENERATION_INTERVAL_SECONDS
    run_worker_pool(interval_seconds=interval or GENERATION_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
