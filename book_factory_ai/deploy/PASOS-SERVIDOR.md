# BackEbook – Pasos en el servidor (Ubuntu + PM2)

Sigue esto después de clonar el proyecto en el servidor.

---

## 1. Entrar al proyecto

```bash
cd /var/www/backebook
# Si clonaste un repo donde BackEbook contiene book_factory_ai:
# cd /var/www/BackEbook/book_factory_ai
```

## 2. Crear y editar `.env`

```bash
cp config/settings.example.env .env
nano .env
```

Pon al menos:

- `FIREBASE_DATABASE_URL=https://tu-proyecto-default-rtdb.firebaseio.com`
- Y deja el archivo `config/serviceAccountKey.json` en su sitio (clave de Firebase del mismo proyecto que ebook-app).

## 3. Instalar PM2 (si no lo tienes)

```bash
sudo apt update
sudo apt install -y nodejs npm
sudo npm install -g pm2
```

## 4. Ejecutar el setup

```bash
bash deploy/setup-ubuntu.sh
```

Si te pide ejecutar un comando para `pm2 startup`, cópialo y ejecútalo (así BackEbook arranca al reiniciar el servidor).

## 5. Comprobar

```bash
pm2 status
curl http://localhost:9753/health
```

## 6. (Opcional) Subdominio con nginx

```bash
sudo cp deploy/nginx-subdomain.conf.example /etc/nginx/sites-available/backebook
sudo nano /etc/nginx/sites-available/backebook   # Cambia server_name a tu subdominio
sudo ln -s /etc/nginx/sites-available/backebook /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

**Comandos útiles (usa `pm2`, no `npm`):**
- `pm2 restart backebook` — reiniciar
- `pm2 logs backebook` — ver logs
- `pm2 stop backebook` — parar

---

### Si sale "Invalid JWT Signature" (Firebase)

1. **Comprobar credenciales en el servidor:**
   ```bash
   cd /root/apps/BackEbook/book_factory_ai
   ./venv/bin/python scripts/verify_firebase.py
   ```
   El script indica si el JSON es válido, si falta algún campo y si la conexión a Firebase funciona.

2. **Revisar la hora del servidor** (si está mal, el JWT falla):
   ```bash
   date -u
   ```
   Si no es correcta: `sudo timedatectl set-ntp true` o ajustar zona/reloj.

3. **Asegurar que usas la clave correcta:**
   - En [Firebase Console](https://console.firebase.google.com) → mismo proyecto que ebook-app → Project settings → Service accounts → **Generate new private key** (usa una clave nueva).
   - Sube el JSON al servidor **sin abrirlo en editores que cambien comillas o codificación** (mejor `scp` o subir el archivo tal cual).
   - Reemplaza `config/serviceAccountKey.json` por ese archivo.

4. **Ruta absoluta en `.env`** (por si el proceso lee otro archivo):
   ```bash
   echo 'FIREBASE_CREDENTIALS_PATH=/root/apps/BackEbook/book_factory_ai/config/serviceAccountKey.json' >> .env
   ```

5. `pm2 restart backebook`
