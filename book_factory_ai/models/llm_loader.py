"""
Carga del modelo de lenguaje una sola vez para reutilizar en análisis, generación y edición.
Compatible con HuggingFace Transformers (ej. Mistral-7B-Instruct).
"""
import logging
from typing import Any, Optional

from config.settings import LLM_MODEL_NAME, DEVICE

logger = logging.getLogger(__name__)

_model = None
_tokenizer = None


def get_model():
    """Devuelve el modelo cargado; lo carga la primera vez."""
    global _model, _tokenizer
    if _model is not None:
        return _model, _tokenizer

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        raise ImportError(
            "Instala transformers y torch: pip install transformers torch"
        ) from None

    logger.info("Cargando modelo %s (device=%s)...", LLM_MODEL_NAME, DEVICE)
    _tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_NAME, trust_remote_code=True)
    _model = AutoModelForCausalLM.from_pretrained(
        LLM_MODEL_NAME,
        device_map=DEVICE,
        trust_remote_code=True,
    )
    _model.eval()
    logger.info("Modelo cargado correctamente.")
    return _model, _tokenizer


def generate_text(
    prompt: str,
    max_new_tokens: int = 512,
    temperature: float = 0.7,
    do_sample: bool = True,
) -> str:
    """
    Genera texto con el modelo cargado.
    """
    model, tokenizer = get_model()
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with __import__("torch").no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=do_sample,
            pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
