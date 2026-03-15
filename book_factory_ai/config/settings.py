"""
Configuración central del sistema BackEbook.
Usa el mismo proyecto Firebase que ebook-app (Realtime Database en APP/eBooks).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

# Rutas del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Firebase (mismo proyecto que ebook-app)
# Crear clave de cuenta de servicio en Firebase Console y poner ruta aquí o en env
FIREBASE_CREDENTIALS_PATH = os.getenv(
    "FIREBASE_CREDENTIALS_PATH",
    os.path.join(BASE_DIR, "config", "serviceAccountKey.json"),
)
# URL de Realtime Database (la misma que usa ebook-app)
def _default_database_url() -> str:
    url = os.getenv("FIREBASE_DATABASE_URL", "").strip()
    if url:
        return url
    # Fallback: construir desde serviceAccountKey.json (project_id)
    try:
        import json
        path = Path(FIREBASE_CREDENTIALS_PATH)
        if not path.is_absolute():
            path = BASE_DIR / path
        if path.exists():
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            pid = data.get("project_id")
            if pid:
                return f"https://{pid}-default-rtdb.firebaseio.com"
    except Exception:
        pass
    return ""

FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL", "").strip() or _default_database_url()

# Ruta en Realtime DB donde ebook-app lee/escribe libros
FIREBASE_BOOKS_PATH = "APP/eBooks"

# Modelo de IA (HuggingFace)
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.2")
# Para pruebas sin GPU se puede usar un modelo más pequeño, ej: "HuggingFaceH4/zephyr-7b-beta"
DEVICE = os.getenv("LLM_DEVICE", "auto")  # "cuda", "cpu", "auto"

# Generación de libros
TARGET_WORDS_PER_BOOK = 80_000
CHAPTERS_PER_BOOK = 20
WORDS_PER_CHAPTER = 4_000

# Workers
WORKERS_GENERATE = int(os.getenv("WORKERS_GENERATE", "15"))
WORKERS_EDIT = int(os.getenv("WORKERS_EDIT", "10"))
MAX_CONCURRENT_BOOKS = 30

# Scheduler (segundos entre inicios de generación)
GENERATION_INTERVAL_SECONDS = int(os.getenv("GENERATION_INTERVAL_SECONDS", "300"))

# Logs
LOG_FILE = LOGS_DIR / "book_generation.log"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Servidor de estado (para despliegue en Ubuntu / subdominio)
SERVER_HOST = os.getenv("BACKEBOOK_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("BACKEBOOK_PORT", "9753"))
