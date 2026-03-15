"""
Configuración del sistema de logs.
Registra libros creados, capítulos, edición y errores en logs/book_generation.log.
"""
import logging
import sys
from pathlib import Path

from config.settings import LOG_FILE, LOG_LEVEL


def setup_logging() -> None:
    """Configura logging a archivo y consola."""
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(fmt, date_fmt))

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(fmt, date_fmt))

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(file_handler)
    root.addHandler(console_handler)
