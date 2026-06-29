# Análisis adversarial del chatbot — y blindaje aplicado

Fecha: 2026-06-29

## Vulnerabilidades encontradas (antes)

El asistente llamaba a un proxy Caddy que reenviaba **todo** el cuerpo del cliente a OpenRouter
con la API key. El control de "quédate en el Plan Perú 2050" vivía en el JavaScript del navegador,
por lo que era inútil ante llamadas directas al endpoint.

| # | Vulnerabilidad | Evidencia | Riesgo |
|---|---|---|---|
| V1 | **Gateway abierto** — aceptaba cualquier `system` prompt | Pedir "receta de torta" → respondía la receta | Uso del LLM como gateway gratuito con la key del dueño |
| V2 | **Modelo arbitrario** | `openai/gpt-4o` respondía | Drenaje del crédito con modelos caros |
| V3 | **Sin rate-limit** | 5 requests = 5×200 | Spam → factura alta |
| V4 | **Guardrail solo en frontend** | El prompt de sistema viajaba desde el cliente | Trivial de saltar |

## Solución aplicada — gateway seguro del lado del servidor

`deploy/gateway/gateway.py` (servicio systemd `pp2050-gw`, en `127.0.0.1:3501`):

- El cliente **solo** envía `{"q": "pregunta"}`. No controla el system prompt, ni el modelo, ni el contexto.
- **System prompt fijo en el servidor**: responde únicamente sobre el Plan Perú 2050; si la pregunta es
  de otro tema, devuelve un mensaje fijo de rechazo. Ignora instrucciones que intenten cambiar su rol.
- **Modelo fijo** (barato) y `max_tokens` acotado, definidos por variable de entorno del servicio.
- **Recuperación server-side**: solo las 2-3 comisiones relevantes (nombre con peso x5 + stopwords).
- **Rate-limit por IP** (ventana deslizante en memoria).
- La **OpenRouter key vive solo en el entorno del servicio** (`/etc/systemd/system/pp2050-gw.service`,
  chmod 600). Se **removió la key del Caddyfile**; Caddy solo hace `reverse_proxy` a `127.0.0.1:3501`.

### Re-test (después)

- V1 receta de torta → «Solo puedo ayudarte con temas del Plan Perú 2050 y sus comisiones.» ✅
- V2 gpt-4o → el servidor fuerza el modelo barato ✅
- V3 `{q}` válido → responde correctamente ✅
- V4 rate-limit → 429 tras el umbral ✅

## Despliegue / operación

```bash
# Subir/actualizar el gateway:
scp deploy/gateway/gateway.py root@VPS:/opt/pp2050-gw/gateway.py
ssh root@VPS systemctl restart pp2050-gw

# La key se setea UNA vez en el unit (Environment=OPENROUTER_KEY=...), chmod 600.
# Caddy: el bloque /api/ia hace reverse_proxy 127.0.0.1:3501 (sin key, sin OpenRouter directo).
```

## Pendiente recomendado
- **Rotar la OpenRouter key** (se compartió por chat). Cambiar `Environment=OPENROUTER_KEY=` en el unit
  + `systemctl restart pp2050-gw`. (Ya no está en el Caddyfile ni en el cliente.)
