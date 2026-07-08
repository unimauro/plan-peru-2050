#!/usr/bin/env bash
# ============================================================
#  Plan Perú 2050 — POLL de deploy (cron en el VPS).
#  Patrón "app viva" de megol/qhaway: el VPS se auto-actualiza con
#  tráfico SALIENTE (git fetch), sin depender de SSH entrante desde
#  datacenter (que Hostinger filtra a ratos). Deploy = push.
#
#  Corre cada ~2 min por cron. Solo deploya si hay commit NUEVO en
#  origin/main; delega en vps-boot.sh (que verifica firma + aplica).
#     */2 * * * * /opt/pp2050/bin/vps-poll.sh >> /var/log/pp2050-deploy.log 2>&1
# ============================================================
set -euo pipefail

REPO="${PP2050_REPO:-/opt/pp2050/repo}"
BOOT="${PP2050_BOOT:-/opt/pp2050/bin/vps-boot.sh}"

git -C "$REPO" fetch --quiet origin main || exit 0   # blip de red: reintenta en el próximo ciclo
LOCAL=$(git -C "$REPO" rev-parse HEAD)
REMOTE=$(git -C "$REPO" rev-parse origin/main)
[ "$LOCAL" = "$REMOTE" ] && exit 0                    # nada nuevo

echo "[$(date -u +%FT%TZ)] commit nuevo ${REMOTE:0:7} — desplegando"
exec "$BOOT"
