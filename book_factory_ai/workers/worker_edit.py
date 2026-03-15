"""
Worker de edición: re-edita libros existentes (opcional).
Puede usarse para mejorar libros ya guardados en Firebase.
"""
import logging
from typing import Any

from core.firebase_client import read_books, save_book
from core.book_editor import edit_book

logger = logging.getLogger(__name__)


def run_edit_worker(book_id: int | None = None) -> dict[str, Any] | None:
    """
    Edita un libro existente en Firebase (por id) o el último.
    Vuelve a guardar en APP/eBooks.
    """
    try:
        raw = read_books()
        if not raw:
            logger.warning("No hay libros para editar.")
            return None

        if book_id is not None:
            bid = str(book_id)
            if bid not in raw:
                logger.warning("Libro id=%s no encontrado.", book_id)
                return None
            book = {**raw[bid], "id": int(bid)}
        else:
            ids = [k for k in raw if str(k).isdigit()]
            if not ids:
                return None
            last_id = max(int(k) for k in ids)
            book = {**raw[str(last_id)], "id": last_id}

        chapters = book.get("chapters") or []
        if not chapters:
            logger.warning("Libro sin capítulos.")
            return None

        chapters = edit_book([c.copy() for c in chapters])
        book["chapters"] = chapters
        save_book(book["id"], book)
        logger.info("Worker edición OK: libro id=%s", book["id"])
        return book
    except Exception as e:
        logger.exception("Worker edición falló: %s", e)
        return None
