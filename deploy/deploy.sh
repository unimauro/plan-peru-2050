#!/usr/bin/env bash
# ============================================================
#  Deploy del Plan Perú 2050 al VPS (Caddy) por rsync.
#  Edita VPS_HOST y VPS_PATH, luego: bash deploy/deploy.sh
# ============================================================
set -euo pipefail

VPS_HOST="${VPS_HOST:-usuario@TU-VPS}"          # ej. carlos@123.45.67.89
VPS_PATH="${VPS_PATH:-/var/www/plan-peru-2050}" # carpeta servida por Caddy

cd "$(dirname "$0")/.."

echo "→ Subiendo sitio a $VPS_HOST:$VPS_PATH"
rsync -az --delete \
  --exclude='.git' \
  --exclude='fuentes' \
  --exclude='scripts' \
  --exclude='deploy' \
  --exclude='entregables/_img' \
  --exclude='.*.mjs' \
  --exclude='ROADMAP.md' \
  ./ "$VPS_HOST:$VPS_PATH/"

echo "✓ Deploy completo."
echo "  Recuerda: en el VPS, recargar Caddy si cambiaste el Caddyfile:  sudo systemctl reload caddy"
