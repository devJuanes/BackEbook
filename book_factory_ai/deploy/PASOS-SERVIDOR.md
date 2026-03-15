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

**Comandos útiles:** `pm2 logs backebook` | `pm2 restart backebook` | `pm2 stop backebook`
