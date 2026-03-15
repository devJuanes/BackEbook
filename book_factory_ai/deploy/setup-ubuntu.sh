#!/bin/bash
# BackEbook - Instalación en Ubuntu con PM2
# Ejecutar DENTRO del proyecto clonado: bash deploy/setup-ubuntu.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$APP_DIR"

echo "==> BackEbook - Setup (PM2)"
echo "    Directorio: $APP_DIR"
echo ""

# Comprobar .env
if [ ! -f "$APP_DIR/.env" ]; then
  echo "ERROR: No existe .env"
  echo "  Copia el ejemplo y edita: cp config/settings.example.env .env"
  echo "  Mínimo: FIREBASE_DATABASE_URL y config/serviceAccountKey.json"
  exit 1
fi

# Dependencias del sistema (Python + Node para PM2)
echo "==> Comprobando dependencias..."
command -v python3 >/dev/null 2>&1 || { echo "Instala Python 3: sudo apt install python3 python3-venv python3-pip"; exit 1; }
if ! command -v pm2 >/dev/null 2>&1; then
  echo "    PM2 no encontrado. Instalando globalmente (npm install -g pm2)..."
  sudo npm install -g pm2 2>/dev/null || {
    echo "    Instala Node y PM2: sudo apt install nodejs npm && sudo npm install -g pm2"
    exit 1
  }
fi

# Venv y dependencias Python
echo "==> Creando venv e instalando dependencias Python..."
python3 -m venv venv
./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r requirements.txt -q

# Crear carpeta logs por si no existe
mkdir -p logs

# PM2: parar si ya estaba corriendo y arrancar
echo "==> Iniciando con PM2..."
pm2 delete backebook 2>/dev/null || true
pm2 start ecosystem.config.cjs

# Guardar lista para que persista al reiniciar
pm2 save

# Inicio automático al arrancar el servidor (solo la primera vez)
if ! pm2 startup 2>/dev/null | grep -q "already"; then
  echo ""
  echo "==> Ejecuta el comando que PM2 te muestre arriba (sudo env PATH=...) para que arranque al reiniciar el servidor."
fi

echo ""
echo "==> Listo. BackEbook está corriendo con PM2."
echo "    Puerto: 9753  →  http://localhost:9753  o  http://TU_IP:9753"
echo ""
echo "Comandos útiles:"
echo "    pm2 status          # estado"
echo "    pm2 logs backebook   # ver logs"
echo "    pm2 restart backebook"
echo "    pm2 stop backebook"
echo ""
echo "Subdominio: ver deploy/nginx-subdomain.conf.example"
echo ""
