#!/usr/bin/env bash
# ============================================================
#  Plan Perú 2050 — apply del deploy EN el VPS (idempotente).
#  Lo dispara GitHub Actions vía SSH (forced-command en
#  authorized_keys → este script). También corre a mano:
#     sudo /opt/pp2050/repo/deploy/vps-apply.sh
#
#  Hace: pull del repo público → sitio estático → gateway.py →
#  unit systemd (con backup+rollback si el servicio no levanta) →
#  reload de Caddy → healthcheck /api/ia. NO toca otros sitios.
# ============================================================
set -euo pipefail

REPO="${PP2050_REPO:-/opt/pp2050/repo}"
WWW="${PP2050_WWW:-/var/www/plan-peru-2050}"
GW_DIR="${PP2050_GW_DIR:-/opt/pp2050-gw}"
UNIT="/etc/systemd/system/pp2050-gw.service"
BK="/opt/pp2050/backup"
mkdir -p "$BK"

echo "→ [1/6] Actualizando repo ($REPO)"
git -C "$REPO" fetch --quiet origin main
git -C "$REPO" reset --hard --quiet origin/main
echo "   commit: $(git -C "$REPO" rev-parse --short HEAD)"

echo "→ [2/6] Sitio estático → $WWW"
rsync -a --delete \
  --exclude='.git' --exclude='.github' --exclude='fuentes' --exclude='scripts' \
  --exclude='deploy' --exclude='entregables/_img' --exclude='.*.mjs' --exclude='ROADMAP.md' \
  "$REPO"/ "$WWW"/

echo "→ [3/6] Backup del estado actual (rollback)"
[ -f "$GW_DIR/gateway.py" ] && cp "$GW_DIR/gateway.py" "$BK/gateway.py.bak"
[ -f "$UNIT" ] && cp "$UNIT" "$BK/pp2050-gw.service.bak"

echo "→ [4/6] gateway.py + unit systemd"
install -D -m644 "$REPO/deploy/gateway/gateway.py" "$GW_DIR/gateway.py"
chmod 755 "$GW_DIR"                      # DynamicUser necesita o+rx para leer el script
unit_changed=0
if ! cmp -s "$REPO/deploy/gateway/pp2050-gw.service" "$UNIT"; then
  cp "$REPO/deploy/gateway/pp2050-gw.service" "$UNIT"
  systemctl daemon-reload
  unit_changed=1
fi

echo "→ [5/6] Reiniciando pp2050-gw"
systemctl restart pp2050-gw || true
sleep 1
if ! systemctl is-active --quiet pp2050-gw; then
  echo "   ✗ El servicio NO levantó — ROLLBACK"
  [ -f "$BK/gateway.py.bak" ] && cp "$BK/gateway.py.bak" "$GW_DIR/gateway.py"
  [ -f "$BK/pp2050-gw.service.bak" ] && cp "$BK/pp2050-gw.service.bak" "$UNIT"
  systemctl daemon-reload
  systemctl restart pp2050-gw || true
  journalctl -u pp2050-gw -n 25 --no-pager || true
  exit 1
fi

echo "→ [6/6] Caddy + healthcheck"
if caddy validate --config /etc/caddy/Caddyfile >/dev/null 2>&1; then
  systemctl reload caddy && echo "   Caddy recargado"
else
  echo "   ⚠ Caddy NO validó — NO se recargó (revisar a mano)"
fi
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 25 -X POST \
  http://127.0.0.1:3501/api/ia -H 'Content-Type: application/json' -d '{"q":"hola"}' || echo 000)
echo "   healthcheck /api/ia → HTTP $code"
case "$code" in
  200|429) echo "✓ Deploy OK";;
  *) echo "   ✗ Healthcheck falló (HTTP $code) — ROLLBACK gateway"
     [ -f "$BK/gateway.py.bak" ] && cp "$BK/gateway.py.bak" "$GW_DIR/gateway.py"
     [ -f "$BK/pp2050-gw.service.bak" ] && cp "$BK/pp2050-gw.service.bak" "$UNIT"
     systemctl daemon-reload; systemctl restart pp2050-gw || true
     exit 1;;
esac
