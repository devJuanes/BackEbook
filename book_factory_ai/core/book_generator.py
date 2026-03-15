"""
Generador de libros: crea índice, capítulos y contenido coherente usando el estilo aprendido.
"""
import logging
import re
from typing import Any

from config.settings import CHAPTERS_PER_BOOK, WORDS_PER_CHAPTER

logger = logging.getLogger(__name__)


def _estimate_words(text: str) -> int:
    return len(text.split())


def generate_book_title(genre: str = "Ficción") -> str:
    """Genera un título para el libro."""
    try:
        from models.llm_loader import generate_text
        prompt = f"Inventa un título de libro atractivo para una obra de {genre}. Solo una línea, sin comillas.\nTítulo:"
        return generate_text(prompt, max_new_tokens=20, temperature=0.8).strip() or "Libro generado"
    except Exception:
        return "Libro generado"


def generate_outline(style: dict[str, Any], genre: str = "Ficción") -> list[str]:
    """Genera el índice (títulos de capítulos) del libro."""
    try:
        from models.llm_loader import generate_text
        prompt = (
            f"Genera exactamente {CHAPTERS_PER_BOOK} títulos de capítulos para un libro de {genre}. "
            "Solo los títulos, uno por línea, numerados como 'Capítulo 1: Título'.\n"
        )
        out = generate_text(prompt, max_new_tokens=400, temperature=0.8)
        lines = [ln.strip() for ln in out.split("\n") if ln.strip()][:CHAPTERS_PER_BOOK]
        # Normalizar formato "Capítulo N: Título"
        result = []
        for i, ln in enumerate(lines):
            if not re.match(r"^Capítulo\s+\d+", ln, re.I):
                ln = f"Capítulo {i+1}: {ln}"
            result.append(ln)
        return result[:CHAPTERS_PER_BOOK]
    except Exception as e:
        logger.warning("Generación de índice con LLM falló: %s. Usando índice por defecto.", e)
        return [f"Capítulo {i+1}: Parte {i+1}" for i in range(CHAPTERS_PER_BOOK)]


def generate_chapter_content(
    chapter_title: str,
    previous_summary: str,
    style_summary: str,
    target_words: int = WORDS_PER_CHAPTER,
) -> str:
    """Genera el contenido de un capítulo manteniendo coherencia con lo anterior."""
    try:
        from models.llm_loader import generate_text
        prompt = (
            f"Estilo a seguir: {style_summary}\n\n"
            f"Resumen de lo anterior en la historia: {previous_summary or 'Inicio del libro.'}\n\n"
            f"Escribe el contenido del siguiente capítulo de un libro (aprox. {target_words} palabras). "
            f"Título del capítulo: {chapter_title}\n\n"
            "Contenido:\n"
        )
        # Pedir más tokens para acercarse a target_words (aprox 1.3 tokens por palabra en español)
        max_tokens = min(2048, int(target_words * 1.5))
        content = generate_text(prompt, max_new_tokens=max_tokens, temperature=0.75)
        return content.strip()
    except Exception as e:
        logger.warning("Generación de capítulo falló: %s.", e)
        return f"[Contenido no generado para: {chapter_title}]"


def generate_book(style: dict[str, Any], genre: str = "Ficción") -> dict[str, Any]:
    """
    Genera un libro completo: título, índice + capítulos.
    Devuelve dict con 'title', 'outline' (lista de títulos de capítulos) y 'chapters'.
    """
    title = generate_book_title(genre)
    outline = generate_outline(style, genre)
    chapters = []
    previous_summary = ""

    for i, title in enumerate(outline):
        logger.info("Generando capítulo %s/%s: %s", i + 1, len(outline), title)
        content = generate_chapter_content(
            title,
            previous_summary,
            style.get("style_summary", "Narrativa en prosa."),
            WORDS_PER_CHAPTER,
        )
        chapters.append({"title": title, "content": content})
        # Resumen breve para coherencia del siguiente capítulo
        previous_summary = content[:500] if len(content) > 500 else content

    return {"title": title, "outline": outline, "chapters": chapters}
