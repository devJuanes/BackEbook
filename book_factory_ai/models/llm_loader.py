"""
Carga del modelo de lenguaje una sola vez para reutilizar en análisis, generación y edición.
Compatible con HuggingFace Transformers.
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
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        raise ImportError(
            "Instala transformers y torch: pip install transformers torch"
        ) from None

    logger.info("Cargando modelo %s (device=%s)...", LLM_MODEL_NAME, DEVICE)

    # Configurar dtype y device_map según el entorno
    if DEVICE == "cuda":
        torch_dtype = torch.float16
        device_map: Any = "auto"
    elif DEVICE == "cpu":
        torch_dtype = torch.float32
        device_map = None  # se moverá todo a CPU más abajo
    else:  # "auto" u otros valores
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        device_map = "auto" if torch.cuda.is_available() else None

    _tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_NAME, trust_remote_code=True)
    _model = AutoModelForCausalLM.from_pretrained(
        LLM_MODEL_NAME,
        torch_dtype=torch_dtype,
        device_map=device_map,
        trust_remote_code=True,
    )

    if DEVICE == "cpu" or (DEVICE not in ("cuda",) and not torch.cuda.is_available()):
        _model.to("cpu")

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
    import torch

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=do_sample,
            pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
