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
  ecosystem.config.cjs         # PM2 (servidor)
  deploy/
    setup-ubuntu.sh             # Instalación en servidor (PM2)
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

## Despliegue en el servidor (Ubuntu + PM2)

Todo listo para **clonar en el servidor y ponerlo a correr con PM2** (puerto **9753**; opcional: subdominio con nginx).

### Pasos en el servidor

**1. Clonar el repo** (o subir el proyecto) en la ruta que quieras, por ejemplo:

```bash
cd /var/www   # o /opt, /home/tu_usuario, etc.
git clone <URL_DEL_REPO> backebook
cd backebook
# Si el repo es solo book_factory_ai, entra: cd book_factory_ai
```

**2. Configurar `.env`**

```bash
cp config/settings.example.env .env
nano .env   # o vim
```

Mínimo necesario:

- `FIREBASE_DATABASE_URL=https://tu-proyecto-default-rtdb.firebaseio.com`
- Tener el archivo `config/serviceAccountKey.json` (clave de cuenta de servicio de Firebase del mismo proyecto que ebook-app).

**3. Instalar y arrancar con PM2**

```bash
bash deploy/setup-ubuntu.sh
```

El script: comprueba Python y PM2, crea el venv, instala dependencias, arranca la app con PM2 y te indica si debes ejecutar `pm2 startup` para que arranque al reiniciar el servidor.

**4. (Opcional) Subdominio con nginx**

Si quieres algo tipo `backebook.tudominio.com`:

```bash
sudo cp deploy/nginx-subdomain.conf.example /etc/nginx/sites-available/backebook
sudo nano /etc/nginx/sites-available/backebook   # cambia server_name
sudo ln -s /etc/nginx/sites-available/backebook /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

HTTPS: `sudo certbot --nginx -d backebook.tudominio.com`

---

**Comandos PM2 útiles**

| Comando | Descripción |
|--------|-------------|
| `pm2 status` | Estado del proceso |
| `pm2 logs backebook` | Ver logs en tiempo real |
| `pm2 restart backebook` | Reiniciar |
| `pm2 stop backebook` | Parar |
| `pm2 save` | Guardar lista (persiste tras reinicio) |

**Servidor HTTP (puerto 9753)**

- `GET /` → estado (JSON)
- `GET /health` → 200 OK (health check)
- `GET /logs` → últimas líneas del log

## Logs

Todo se registra en `logs/book_generation.log`: libros creados, capítulos generados, edición y errores.

## Workers y rendimiento

- `WORKERS_GENERATE` y `WORKERS_EDIT` en `config/settings.py` (o variables de entorno).
- El sistema está pensado para escalar hasta muchos workers; en la práctica, limitar por RAM/GPU según el modelo.
