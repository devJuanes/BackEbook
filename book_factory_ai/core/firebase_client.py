"""
Cliente Firebase para BackEbook.
Conecta al mismo Firebase que usa ebook-app: Realtime Database en APP/eBooks.
Lee libros existentes como referencia y escribe los nuevos para que la app los muestre.
"""
import logging
from typing import Any

from config.settings import (
    FIREBASE_CREDENTIALS_PATH,
    FIREBASE_DATABASE_URL,
    FIREBASE_BOOKS_PATH,
)

logger = logging.getLogger(__name__)

# Inicialización diferida de Firebase
_firebase_app = None
_db = None


def _init_firebase() -> None:
    """Inicializa Firebase Admin con las credenciales del proyecto ebook-app."""
    global _firebase_app, _db
    if _firebase_app is not None:
        return

    try:
        import firebase_admin
        from firebase_admin import credentials, db as firebase_db
    except ImportError:
        raise ImportError(
            "Instala firebase-admin: pip install firebase-admin"
        ) from None

    if not FIREBASE_DATABASE_URL:
        raise ValueError(
            "FIREBASE_DATABASE_URL debe estar definido (ej. en .env o config). "
            "Usa la misma URL de Realtime Database que ebook-app."
        )

    if not FIREBASE_CREDENTIALS_PATH or not __import__("os").path.isfile(FIREBASE_CREDENTIALS_PATH):
        raise FileNotFoundError(
            f"Credenciales de Firebase no encontradas en {FIREBASE_CREDENTIALS_PATH}. "
            "Descarga la clave de cuenta de servicio desde Firebase Console (mismo proyecto que ebook-app)."
        )

    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    _firebase_app = firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DATABASE_URL})
    _db = firebase_db.reference()
    logger.info("Firebase inicializado (Realtime Database, mismo proyecto que ebook-app)")


def get_db():
    """Devuelve la referencia raíz de Realtime Database."""
    _init_firebase()
    return _db


def read_books() -> dict[str, Any]:
    """
    Lee todos los libros desde APP/eBooks (misma ruta que usa ebook-app).
    Returns:
        Diccionario id -> datos del libro (title, author, chapters, etc.)
    """
    ref = get_db().child(FIREBASE_BOOKS_PATH)
    snapshot = ref.get()
    if snapshot is None:
        return {}
    return snapshot or {}


def get_next_book_id() -> int:
    """Calcula el siguiente id numérico para un libro nuevo."""
    books = read_books()
    if not books:
        return 1
    if isinstance(books, list):
        ids = []
        for v in books:
            if isinstance(v, dict):
                try:
                    bid = v.get("id")
                    if bid is not None:
                        ids.append(int(bid))
                except (TypeError, ValueError):
                    pass
    else:
        ids = [int(k) for k in books.keys() if str(k).isdigit()]
    return max(ids) + 1 if ids else 1


def save_book(book_id: int, book_data: dict[str, Any]) -> None:
    """
    Guarda un libro en APP/eBooks/{id} para que ebook-app lo muestre.
    book_data debe seguir el esquema de la app: id, title, author, cover, color,
    genre, rating, pages, slug, chapters (lista de {title, content}).
    """
    ref = get_db().child(FIREBASE_BOOKS_PATH).child(str(book_id))
    ref.set(book_data)
    logger.info("Libro guardado en Firebase: id=%s, title=%s", book_id, book_data.get("title"))
