# Deploy en VPS con Caddy

El sitio es **estático** (~2.5 MB). Solo hay que copiar archivos + un bloque en el Caddyfile.
La **Consulta IA** se sirve por un proxy de Caddy que mantiene la API key del lado del servidor.

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

## 3. Key de IA (oculta)

Pon la key de OpenRouter en el entorno del servicio Caddy (NO en el repo):

```bash
sudo systemctl edit caddy
```
Y agrega:
```ini
[Service]
Environment=OPENROUTER_KEY=sk-or-v1-XXXXXXXX
```
Luego:
```bash
sudo systemctl daemon-reload
sudo systemctl reload caddy
```

El dashboard llama a `/api/ia`; Caddy lo reescribe a `openrouter.ai/api/v1/chat/completions`
e inyecta `Authorization: Bearer {OPENROUTER_KEY}`. La key nunca llega al navegador.

> Modelo: se define en `config.js` (`window.PP2050_IA.model`). Si el proxy no responde,
> el asistente cae automáticamente a búsqueda local sobre los datos (no se rompe).

## 4. DNS

Apunta el dominio/subdominio (registro A) a la IP del VPS. Caddy emite el certificado al primer acceso.

## Actualizaciones

Cada vez que cambien datos o documentos: `git push` (mantiene el versionado) y luego `bash deploy/deploy.sh`.
