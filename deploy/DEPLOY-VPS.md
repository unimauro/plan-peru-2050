# Deploy en VPS con Caddy

El sitio es **estático** (~2.5 MB). Solo hay que copiar archivos + un bloque en el Caddyfile.
La **Consulta IA** se sirve a través del **gateway seguro `pp2050-gw`** (systemd, `127.0.0.1:3501`),
que fija system prompt, modelo, tope de tokens, rate-limit y cap global de costo. Caddy solo hace
`reverse_proxy` al gateway; **la API key vive únicamente en el gateway**, nunca en Caddy ni en el cliente.

> ⚠️ **No** configures Caddy con `reverse_proxy https://openrouter.ai` + la key: eso convierte
> `/api/ia` en un **proxy abierto y anónimo pagado con tu key** (cualquiera elige modelo caro y
> `max_tokens` alto → factura arbitraria; sin system prompt ni rate-limit). Siempre a través del gateway.

## 1. Subir el sitio

Edita `VPS_HOST` y `VPS_PATH` en `deploy/deploy.sh` y ejecuta:

```bash
bash deploy/deploy.sh
# o:  VPS_HOST=carlos@tu-vps VPS_PATH=/var/www/plan-peru-2050 bash deploy/deploy.sh
```

(Sube todo menos `fuentes/`, `scripts/`, `deploy/` y archivos de trabajo.)

## 2. Caddyfile

Copia el bloque de `deploy/Caddyfile.snippet` a `/etc/caddy/Caddyfile`, ajustando el dominio.
Caddy gestiona el HTTPS (Let's Encrypt) automáticamente.

## 3. Gateway de IA seguro + key (oculta)

La key vive en un archivo aparte con permisos `600` (NO en el repo, NO en el unit, NO en Caddy):

```bash
sudo install -m600 /dev/stdin /etc/pp2050-gw.env <<'EOF'
OPENROUTER_KEY=sk-or-v1-XXXXXXXX
# Opcional, aún más barato (Gemini nativo):
# GEMINI_API_KEY=AIza...
EOF
```

Instala y arranca el gateway:
```bash
sudo mkdir -p /opt/pp2050-gw
sudo cp deploy/gateway/gateway.py /opt/pp2050-gw/
sudo cp deploy/gateway/pp2050-gw.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now pp2050-gw
sudo systemctl status pp2050-gw    # debe quedar active (running) en :3501
```

Caddy enruta `/api/ia → 127.0.0.1:3501` (ver `Caddyfile.snippet`). El cliente solo manda `{"q":"..."}`;
el gateway fija system prompt/modelo/tope de tokens, rate-limit por IP (IP real de Caddy, no spoofeable),
cap global diario (`PP2050_DAILY_MAX`) y CORS por dominio (`PP2050_ALLOWED_ORIGINS`). La key nunca sale del gateway.

> **Además, pon un hard-cap de gasto mensual en el panel de OpenRouter** — última línea de defensa de costo.
>
> Modelo: se define por env en el unit (`PP2050_MODELS` / `GEMINI_*`). Si el gateway no responde,
> el asistente cae automáticamente a búsqueda local sobre los datos (no se rompe).

## 4. DNS

Apunta el dominio/subdominio (registro A) a la IP del VPS. Caddy emite el certificado al primer acceso.

## Actualizaciones

**Auto-deploy por POLL en el VPS** (patrón "app viva" de megol/qhaway), con **verificación de firma**.
Solo tráfico SALIENTE del VPS (no depende de SSH entrante desde datacenter, que Hostinger filtra a ratos).
Flujo: `push` (commit **firmado** con SSH) → un **cron cada ~2 min** corre `/opt/pp2050/bin/vps-poll.sh`
→ `git fetch`; si hay commit nuevo en `origin/main` → llama al **bootstrap** `/opt/pp2050/bin/vps-boot.sh`
(root:root 700, fuera del repo): `flock` → **`git verify-commit`** contra `allowed_signers` (si la firma
no es de confianza, **ABORTA**) → `git reset --hard` → `deploy/vps-apply.sh` (sitio + `gateway.py` + unit,
con **backup/rollback** y healthcheck). Comprometer GitHub no basta: sin la llave de **firma** no hay deploy.

Forzar deploy YA (sin esperar el cron): en el VPS `sudo /opt/pp2050/bin/vps-boot.sh`, o desde tu laptop
`ssh -i ~/.ssh/pp2050_deploy root@VPS` (la deploy key tiene forced-command al bootstrap).

### Setup una sola vez (en el VPS)

```bash
# 1) Clon del repo público
sudo mkdir -p /opt/pp2050 && sudo git clone https://github.com/unimauro/plan-peru-2050.git /opt/pp2050/repo

# 2) Llave (rotada) en archivo 600 — NO en el unit
sudo install -m600 /dev/stdin /etc/pp2050-gw.env <<'EOF'
OPENROUTER_KEY=sk-or-v1-NUEVA_KEY_ROTADA
EOF

# 3) Firmantes de confianza (email + llave pública SSH con la que firmas los commits)
echo "unimauro@gmail.com ssh-ed25519 AAAA..." | sudo tee /opt/pp2050/allowed_signers

# 4) Bootstrap inmutable fuera del repo + permisos estrictos
sudo install -o root -g root -m700 /opt/pp2050/repo/deploy/vps-boot.sh /opt/pp2050/bin/vps-boot.sh
sudo chown -R root:root /opt/pp2050 && sudo chmod -R go-w /opt/pp2050

# 5) Poll por cron (auto-deploy) + bootstrap fuera del repo
sudo install -o root -g root -m700 /opt/pp2050/repo/deploy/vps-poll.sh /opt/pp2050/bin/vps-poll.sh
( sudo crontab -l 2>/dev/null; echo '*/2 * * * * /opt/pp2050/bin/vps-poll.sh >> /var/log/pp2050-deploy.log 2>&1' ) | sudo crontab -

# 6) (opcional) Deploy key para forzar deploy desde tu laptop, con forced-command → bootstrap:
#    restrict,command="/opt/pp2050/bin/vps-boot.sh" ssh-ed25519 AAAA... pp2050-deploy
sudo nano /root/.ssh/authorized_keys
```

En tu máquina, firma los commits de este repo:
`git config gpg.format ssh; git config user.signingkey ~/.ssh/id_ed25519.pub; git config commit.gpgsign true`
