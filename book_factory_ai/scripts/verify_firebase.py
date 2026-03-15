#!/usr/bin/env python3
"""
Comprueba en el servidor que serviceAccountKey.json sea válido y que Firebase responda.
Ejecutar: cd book_factory_ai && ./venv/bin/python scripts/verify_firebase.py
"""
import sys
from pathlib import Path

# Raíz del proyecto
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

def main():
    import os
    import datetime
    from config.settings import FIREBASE_CREDENTIALS_PATH, FIREBASE_DATABASE_URL

    print("Hora del servidor (debe ser correcta para JWT):", datetime.datetime.utcnow().isoformat() + "Z")
    print("Ruta de credenciales:", FIREBASE_CREDENTIALS_PATH)
    print("Existe archivo:", os.path.isfile(FIREBASE_CREDENTIALS_PATH))
    print("Database URL:", FIREBASE_DATABASE_URL or "(no definida)")

    if not os.path.isfile(FIREBASE_CREDENTIALS_PATH):
        print("ERROR: No se encuentra el archivo de credenciales.")
        return 1

    # Cargar JSON y comprobar campos
    try:
        import json
        with open(FIREBASE_CREDENTIALS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        need = ["type", "project_id", "private_key_id", "private_key", "client_email"]
        missing = [k for k in need if not data.get(k)]
        if missing:
            print("ERROR: Al archivo le faltan campos:", missing)
            return 1
        print("project_id:", data.get("project_id"))
        print("client_email:", data.get("client_email"))
        pk = data.get("private_key", "")
        if "BEGIN PRIVATE KEY" not in pk or "END PRIVATE KEY" not in pk:
            print("ERROR: private_key no parece un PEM válido (debe contener BEGIN/END PRIVATE KEY).")
            return 1
        # Los \n en el JSON deben ser literales \n (dos caracteres); al cargar se convierten en newline
        if len(pk) < 100:
            print("ERROR: private_key demasiado corto (posible clave truncada o mal pegada).")
            return 1
        print("private_key: longitud OK")
    except json.JSONDecodeError as e:
        print("ERROR: El archivo no es un JSON válido:", e)
        return 1

    # Intentar inicializar Firebase y leer algo
    try:
        import firebase_admin
        from firebase_admin import credentials, db as firebase_db
    except ImportError:
        print("ERROR: firebase-admin no instalado. Activa el venv y pip install -r requirements.txt")
        return 1

    try:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        app = firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DATABASE_URL})
        ref = firebase_db.reference("APP/eBooks")
        ref.get()
        print("OK: Firebase conectado y lectura de APP/eBooks correcta.")
        firebase_admin.delete_app(app)
        return 0
    except Exception as e:
        print("ERROR al conectar con Firebase:", type(e).__name__, str(e))
        return 1

if __name__ == "__main__":
    sys.exit(main())
