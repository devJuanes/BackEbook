"""
Pipeline de generación: leer libros desde Firebase → analizar → generar → editar → guardar.
"""
import logging
from typing import Any

from core.firebase_client import read_books, get_next_book_id, save_book
from core.book_analyzer import analyze_books
from core.book_generator import generate_book
from core.book_editor import edit_book

logger = logging.getLogger(__name__)

# Metadatos por defecto compatibles con ebook-app
DEFAULT_COVER = "https://images.unsplash.com/photo-1544947950-fa07a98d237f"
DEFAULT_COLOR = "#2E2D88"
DEFAULT_GENRE = "Ficción"
DEFAULT_RATING = 4.5
DEFAULT_AUTHOR = "BackEbook IA"


def _slug_from_title(title: str) -> str:
    """Genera un slug para la URL (compatible con ebook-app)."""
    import unicodedata
    s = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    s = "".join(c if c.isalnum() or c in " -" else "" for c in s)
    return "-".join(s.lower().split())[:80]


def run_pipeline(genre: str = DEFAULT_GENRE) -> dict[str, Any] | None:
    """
    Ejecuta el pipeline completo:
    1. Leer libros desde Firebase (APP/eBooks)
    2. Analizar estilo
    3. Generar índice y capítulos
    4. Editar capítulos
    5. Ensamblar y guardar en Firebase (mismo path para ebook-app)
    """
    try:
        raw = read_books()
        # Firebase puede devolver dict (id -> libro) o list (array indexado)
        if isinstance(raw, list):
            books_list = [
                {**v, "id": v.get("id", i)} for i, v in enumerate(raw)
                if isinstance(v, dict) and (v.get("chapters") or v.get("title"))
            ]
        elif isinstance(raw, dict):
            books_list = [
                {**v, "id": int(k)} for k, v in raw.items()
                if isinstance(v, dict) and (v.get("chapters") or v.get("title"))
            ]
        else:
            books_list = []
    except Exception as e:
        logger.exception("Error leyendo libros desde Firebase: %s", e)
        return None

    style = analyze_books(books_list)
    logger.info("Estilo analizado: %s", style.get("style_summary", "")[:100])

    generated = generate_book(style, genre)
    chapters = generated["chapters"]
    if not chapters:
        logger.error("No se generaron capítulos.")
        return None

    logger.info("Editando %s capítulos...", len(chapters))
    chapters = edit_book(chapters)

    # Calcular páginas aproximadas (250 palabras por página)
    total_words = sum(len((ch.get("content") or "").split()) for ch in chapters)
    title = generated.get("title") or "Libro generado por BackEbook"

    book_id = get_next_book_id()
    book_data = {
        "id": book_id,
        "title": title,
        "author": DEFAULT_AUTHOR,
        "cover": DEFAULT_COVER,
        "color": DEFAULT_COLOR,
        "genre": genre,
        "rating": DEFAULT_RATING,
        "pages": max(1, total_words // 250),
        "slug": _slug_from_title(title) or f"libro-{book_id}",
        "chapters": chapters,
    }

    try:
        save_book(book_id, book_data)
    except Exception as e:
        logger.exception("Error guardando libro en Firebase: %s", e)
        return None

    logger.info("Pipeline completado. Libro id=%s, palabras≈%s", book_id, total_words)
    return book_data
