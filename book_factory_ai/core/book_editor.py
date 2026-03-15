"""
Editor de libros: corrige gramática, mejora coherencia, elimina repeticiones y claridad.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


def edit_text(text: str) -> str:
    """
    Pasa el texto por el modelo para corrección/mejora de gramática, coherencia y claridad.
    """
    if not text or not text.strip():
        return text

    try:
        from models.llm_loader import generate_text
        prompt = (
            "Reescribe el siguiente fragmento de libro mejorando gramática, coherencia y claridad. "
            "Elimina repeticiones innecesarias. Mantén el mismo tono y longitud aproximada. "
            "Solo devuelve el texto reescrito, sin explicaciones.\n\n"
            f"{text[:3000]}\n\n"
            "Texto mejorado:\n"
        )
        edited = generate_text(prompt, max_new_tokens=1024, temperature=0.3)
        return edited.strip() or text
    except Exception as e:
        logger.warning("Edición con LLM no disponible: %s. Devolviendo texto original.", e)
        return text


def edit_chapter(chapter: dict[str, Any]) -> dict[str, Any]:
    """Edita el contenido de un capítulo (solo el campo content)."""
    content = chapter.get("content") or ""
    if not content.strip():
        return chapter
    # Editar por bloques si es muy largo para no exceder contexto
    block_size = 1500
    if len(content) <= block_size:
        chapter["content"] = edit_text(content)
        return chapter

    parts = []
    start = 0
    while start < len(content):
        end = min(start + block_size, len(content))
        # Cortar en fin de párrafo si es posible
        if end < len(content):
            last_break = content.rfind("\n\n", start, end + 1)
            if last_break > start:
                end = last_break + 2
        parts.append(edit_text(content[start:end]))
        start = end
    chapter["content"] = "\n\n".join(parts)
    return chapter


def edit_book(chapters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Edita todos los capítulos del libro."""
    return [edit_chapter(ch.copy()) for ch in chapters]
