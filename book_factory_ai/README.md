# BackEbook – Fábrica de generación de libros

Sistema en Python que genera y edita libros de forma automática y continua, usando como referencia los libros ya almacenados en **el mismo Firebase que usa ebook-app**.

## Arquitectura

- **Firebase**: Mismo proyecto que **ebook-app**. Se usa **Realtime Database** en la ruta `APP/eBooks`: se leen libros existentes para analizar estilo y se escriben los nuevos ahí para que la app los muestre.
- **Pipeline**: Leer libros → Analizar estilo → Generar índice y capítulos → Editar → Guardar en Firebase.

## Estructura del proyecto

```
book_factory_ai/
  core/
    firebase_client.py   # Conexión a Firebase (Realtime DB APP/eBooks)
    book_analyzer.py     # Análisis de estilo y estructura de libros
    book_generator.py    # Generación de índice y capítulos
    book_editor.py       # Corrección y mejora de texto
    pipeline.py          # Orquestación del flujo completo
    log_config.py        # Configuración de logs
  workers/
    worker_manager.py    # Administrador de workers (paralelo)
    worker_generate.py   # Worker que ejecuta el pipeline
    worker_edit.py       # Worker de re-edición de libros
  models/
    llm_loader.py        # Carga única del modelo (HuggingFace)
  config/
    settings.py          # Configuración (Firebase, workers, rutas)
  logs/                  # book_generation.log
  main.py              # Worker solo (main.py --once o bucle)
  server.py            # Worker + HTTP en puerto 9753 (despliegue)
  requirements.txt
  deploy/
    backebook.service           # systemd (Ubuntu)
    setup-ubuntu.sh             # Instalación en servidor
    nginx-subdomain.conf.example  # Nginx para subdominio
```

## Configuración Firebase (mismo que ebook-app)

1. En [Firebase Console](https://console.firebase.google.com) del proyecto de **ebook-app**:
   - Crear una **cuenta de servicio** (Project settings → Service accounts → Generate new private key).
2. Guardar el JSON como `config/serviceAccountKey.json` (o otra ruta y definir `FIREBASE_CREDENTIALS_PATH`).
3. Definir la URL de Realtime Database (la misma que usa la app), por ejemplo:
   - Variable de entorno: `FIREBASE_DATABASE_URL=https://TU_PROYECTO-default-rtdb.firebaseio.com`
   - O en `config/settings.py`: asignar `FIREBASE_DATABASE_URL`.

Los libros generados se guardan en `APP/eBooks/{id}` con el mismo esquema que usa ebook-app: `id`, `title`, `author`, `cover`, `color`, `genre`, `rating`, `pages`, `slug`, `chapters` (lista de `{title, content}`).

## Modelo de IA

Por defecto se usa un modelo compatible con HuggingFace (ej. `mistralai/Mistral-7B-Instruct-v0.2`). Para pruebas sin GPU se puede usar un modelo más pequeño en `config/settings.py` o con `LLM_MODEL_NAME`.

## Uso local

```bash
cd book_factory_ai
pip install -r requirements.txt
# Configurar FIREBASE_DATABASE_URL y serviceAccountKey.json

# Una sola generación (pruebas)
python main.py --once

# Ejecución continua (generación cada N segundos)
python main.py
python main.py --interval 600
```

## Despliegue en Ubuntu (servidor + subdominio)

BackEbook puede correr en un servidor Ubuntu con un **puerto dedicado** (por defecto **9753**) y un **subdominio** opcional (ej. `backebook.tudominio.com`).

### 1. Servidor con puerto y worker en segundo plano

- **`server.py`**: inicia el worker de generación en segundo plano y un servidor HTTP en el puerto **9753** (configurable con `BACKEBOOK_PORT`).
- Rutas:
  - `GET /` → estado del servicio (JSON).
  - `GET /health` → 200 OK (para balanceadores o health checks).
  - `GET /logs` → últimas líneas del log.

```bash
# Probar en local
python server.py
# Abre http://localhost:9753
```

### 2. Variables de entorno en servidor

En `.env` del proyecto (o en el systemd `EnvironmentFile`):

- `FIREBASE_DATABASE_URL` y `FIREBASE_CREDENTIALS_PATH` (o `serviceAccountKey.json` en `config/`).
- Opcional: `BACKEBOOK_HOST=0.0.0.0`, `BACKEBOOK_PORT=9753`.

### 3. Instalación en Ubuntu (systemd)

En el servidor, clona o copia el proyecto y ejecuta:

```bash
cd /opt/backebook   # o la ruta donde esté el proyecto
sudo bash deploy/setup-ubuntu.sh
```

El script:

- Instala dependencias (python3, venv, pip).
- Crea el venv e instala `requirements.txt`.
- Instala y habilita el servicio **backebook** (systemd).
- El servicio ejecuta `server.py` (puerto 9753 + worker).

Comandos útiles:

```bash
sudo systemctl status backebook
sudo systemctl restart backebook
journalctl -u backebook -f
```

### 4. Subdominio con nginx

- Copia `deploy/nginx-subdomain.conf.example` a `/etc/nginx/sites-available/backebook`.
- Edita `server_name` (ej. `backebook.tudominio.com`) y el upstream si cambiaste el puerto.
- Habilita el sitio y recarga nginx:

```bash
sudo ln -s /etc/nginx/sites-available/backebook /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

Opcional: HTTPS con Let's Encrypt (`certbot --nginx -d backebook.tudominio.com`); en el ejemplo hay comentarios para el `server` 443.

## Logs

Todo se registra en `logs/book_generation.log`: libros creados, capítulos generados, edición y errores.

## Workers y rendimiento

- `WORKERS_GENERATE` y `WORKERS_EDIT` en `config/settings.py` (o variables de entorno).
- El sistema está pensado para escalar hasta muchos workers; en la práctica, limitar por RAM/GPU según el modelo.
