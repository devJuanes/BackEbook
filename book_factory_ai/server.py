"""
Servidor de estado BackEbook: expone un puerto para health/status y ejecuta
el worker de generación en segundo plano. Para despliegue en Ubuntu con subdominio.
"""
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.log_config import setup_logging

setup_logging()

import logging
from config.settings import SERVER_HOST, SERVER_PORT, LOG_FILE

logger = logging.getLogger(__name__)

# Estado global (worker en background)
_started_at = None
_worker_thread = None


def _run_worker() -> None:
    """Ejecuta el bucle de generación en un hilo."""
    global _started_at
    _started_at = time.time()
    try:
        from workers.worker_manager import run_worker_pool
        run_worker_pool()
    except Exception as e:
        logger.exception("Worker terminó con error: %s", e)


def create_app():
    from flask import Flask, jsonify
    app = Flask(__name__)

    @app.route("/")
    def index():
        uptime = (time.time() - _started_at) if _started_at else 0
        return jsonify({
            "service": "BackEbook",
            "status": "running",
            "uptime_seconds": round(uptime),
            "port": SERVER_PORT,
        })

    @app.route("/health")
    def health():
        return jsonify({"ok": True}), 200

    @app.route("/logs")
    def logs():
        """Últimas líneas del log (solo lectura)."""
        try:
            if LOG_FILE.exists():
                with open(LOG_FILE, encoding="utf-8") as f:
                    lines = f.readlines()
                last = lines[-50:] if len(lines) > 50 else lines
                return jsonify({"lines": last})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        return jsonify({"lines": []})

    return app


def main() -> None:
    global _worker_thread
    logger.info("Iniciando BackEbook server en %s:%s (worker en segundo plano)", SERVER_HOST, SERVER_PORT)

    _worker_thread = threading.Thread(target=_run_worker, daemon=True)
    _worker_thread.start()

    app = create_app()
    app.run(host=SERVER_HOST, port=SERVER_PORT, threaded=True, use_reloader=False)


if __name__ == "__main__":
    main()
