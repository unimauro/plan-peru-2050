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
  proxy: "",
  model: "meta-llama/llama-3.3-70b-instruct:free",
  endpoint: "https://openrouter.ai/api/v1/chat/completions",
};
