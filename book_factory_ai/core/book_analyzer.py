"""
Analizador de libros: lee libros desde Firebase, detecta estilo, estructura y temas.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


def _extract_text_sample(books: list[dict[str, Any]], max_chars: int = 15000) -> str:
    """Extrae una muestra de texto de varios libros para análisis."""
    samples = []
    total = 0
    for book in books:
        chapters = book.get("chapters") or []
        for ch in chapters:
            content = (ch.get("content") or "").strip()
            if not content:
                continue
            samples.append(content)
            total += len(content)
            if total >= max_chars:
                return "\n\n".join(samples)
    return "\n\n".join(samples)


def analyze_books(books: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Analiza una lista de libros y devuelve un resumen estructurado del estilo.
    Incluye: temas recurrentes, estructura típica (capítulos), tono y resumen de estilo.
    """
    if not books:
        return {
            "style_summary": "Sin libros de referencia.",
            "typical_structure": {"chapters": 0},
            "main_themes": [],
            "tone": "neutral",
        }

    # Estructura: contar capítulos y longitudes
    chapter_counts = []
    for b in books:
        chs = b.get("chapters") or []
        chapter_counts.append(len(chs))

    avg_chapters = sum(chapter_counts) / len(chapter_counts) if chapter_counts else 0
    sample_text = _extract_text_sample(books)

    # Opcional: usar LLM para resumir estilo (si hay mucho texto, se puede truncar en el prompt)
    style_summary = "Narrativa en prosa; capítulos con título y contenido desarrollado."
    main_themes: list[str] = []
    tone = "narrativo"

    try:
        from models.llm_loader import generate_text
        prompt = (
            "Analiza brevemente el estilo de escritura del siguiente fragmento de libro. "
            "Responde en una sola frase: tono (ej. narrativo, dramático), y tipo de prosa.\n\n"
            f"Fragmento:\n{sample_text[:2000]}\n\nEstilo:"
        )
        style_summary = generate_text(prompt, max_new_tokens=80, temperature=0.3).strip()
    except Exception as e:
        logger.warning("Análisis con LLM no disponible: %s. Usando resumen por defecto.", e)

    return {
        "style_summary": style_summary,
        "typical_structure": {
            "chapters": round(avg_chapters),
            "chapter_counts": chapter_counts,
        },
        "main_themes": main_themes,
        "tone": tone,
        "sample_length": len(sample_text),
    }
