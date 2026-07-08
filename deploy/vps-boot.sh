#!/usr/bin/env bash
# ============================================================
#  Plan Perú 2050 — BOOTSTRAP de deploy (entrypoint del forced-command).
#
#  IMPORTANTE: la copia que EJECUTA el forced-command debe vivir FUERA del
#  repo y ser root:root 0700 e INMUTABLE por git (este archivo es solo la
#  fuente versionada; se instala a mano en /opt/pp2050/bin/vps-boot.sh).
#  Así un commit malicioso NO puede reescribir el entrypoint que corre root.
#
#  Hace, como root: lock exclusivo → fetch → VERIFICA FIRMA del commit de
#  origin/main contra allowed_signers → reset --hard → ejecuta el deploy.
#  Si la firma no es de confianza, ABORTA (no despliega).
# ============================================================
set -euo pipefail

REPO="${PP2050_REPO:-/opt/pp2050/repo}"
SIGNERS="${PP2050_ALLOWED_SIGNERS:-/opt/pp2050/allowed_signers}"

# Un solo deploy a la vez (Actions + manual no se pisan)
exec 9>/run/pp2050-apply.lock
flock -n 9 || { echo "✗ Otro deploy en curso"; exit 1; }

[ -d "$REPO/.git" ] || { echo "✗ $REPO no es un repo git"; exit 1; }

echo "→ [0/6] Verificando firma del commit a desplegar"
git -C "$REPO" fetch --quiet origin main
git -C "$REPO" config gpg.format ssh
git -C "$REPO" config gpg.ssh.allowedSignersFile "$SIGNERS"
if ! git -C "$REPO" verify-commit origin/main 2>/tmp/verify.err; then
  echo "✗ El commit origin/main NO tiene una firma de confianza — ABORTA deploy"
  cat /tmp/verify.err 2>/dev/null || true
  exit 1
fi
echo "   ✓ firma válida: $(git -C "$REPO" log -1 --format='%h %GS')"
git -C "$REPO" reset --hard --quiet origin/main

# El script de deploy ya está verificado (viene de un commit firmado): ejecutarlo.
exec /usr/bin/env PP2050_VERIFIED=1 bash "$REPO/deploy/vps-apply.sh"
