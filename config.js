// ============================================================
//  Plan Perú 2050 — Configuración del asistente de IA (opcional)
//
//  El dashboard funciona 100% sin IA. Si quieres habilitar el
//  "Consulta IA" sobre el plan, configura UNA de estas opciones:
//
//  OPCIÓN A (segura): despliega un proxy (ver proyecto-inti/proxy-vercel)
//  y pon su URL en "proxy". La API key NO queda pública.
//
//  OPCIÓN B (demo): pon tu "apiKey" de OpenRouter aquí. ⚠️ Quedará
//  VISIBLE en el sitio estático. Usa una key con límite bajo / modelo :free.
//
//  Si ambos quedan vacíos, el asistente responde con búsqueda local
//  sobre los datos de las comisiones (sin LLM).
// ============================================================
window.PP2050_IA = {
  apiKey: "",
  // En el VPS (Caddy) el proxy /api/ia inyecta la key del lado del servidor.
  // Si la ruta no existe (ej. GitHub Pages), el asistente cae a búsqueda local.
  proxy: "/api/ia",
  model: "meta-llama/llama-3.3-70b-instruct:free",
  endpoint: "https://openrouter.ai/api/v1/chat/completions",
};

// ============================================================
//  Dosificación de la entrega por hito (feature stage).
//  Se controla por la variable de URL ?v=  (tiene prioridad).
//   ?v=all   → muestra TODO (validadas + en revisión)
//   ?v=validado → solo comisiones validadas, todas las secciones
//   ?v=h1    → Hito 1: directorio + mapa + simulador + panorama
//   ?v=h2    → Hito 2: lo de h1 + plan de 100 días
//   ?v=h3    → Hito 3: todo
//  "default" es lo que se ve cuando NO hay ?v= en la URL.
//  Cámbialo a "h1"/"h2"/"h3"/"validado" para dosificar lo que ve el CIP.
// ============================================================
window.PP2050_STAGE = {
  default: "all",
};
