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

**Auto-deploy en cada push a `main`** (GitHub Actions → VPS). Ver `.github/workflows/deploy.yml`
y `deploy/vps-apply.sh`. El flujo: push → Actions hace SSH al VPS con una **deploy key** cuyo
`authorized_keys` tiene *forced-command* (solo ejecuta `vps-apply.sh`, no da shell) → el VPS hace
`git pull`, actualiza sitio + `gateway.py` + unit (con **backup y rollback** si el servicio no
levanta), recarga Caddy y hace healthcheck de `/api/ia`.

Deploy manual (fallback): `bash deploy/deploy.sh` (solo estático) o, en el VPS,
`sudo /opt/pp2050/repo/deploy/vps-apply.sh` (completo).

### Setup una sola vez (en el VPS)

```bash
# 1) Clon del repo público (sin credenciales)
sudo mkdir -p /opt/pp2050 && sudo git clone https://github.com/unimauro/plan-peru-2050.git /opt/pp2050/repo

# 2) Llave (rotada) en archivo 600 — NO en el unit
sudo install -m600 /dev/stdin /etc/pp2050-gw.env <<'EOF'
OPENROUTER_KEY=sk-or-v1-NUEVA_KEY_ROTADA
EOF

# 3) Deploy key con forced-command (pega la PÚBLICA de la deploy key):
#    command="/opt/pp2050/repo/deploy/vps-apply.sh",no-pty,no-port-forwarding,no-agent-forwarding,no-X11-forwarding ssh-ed25519 AAAA... pp2050-deploy
sudo nano /root/.ssh/authorized_keys
```

En GitHub (repo → Settings → Secrets → Actions): `VPS_HOST`, `VPS_DEPLOY_KEY` (privada), `VPS_KNOWN_HOSTS`.
