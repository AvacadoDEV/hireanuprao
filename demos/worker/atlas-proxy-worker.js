// Cloudflare Worker — proxies the Atlas/Nova demo's chat calls to Anthropic.
//
// Deploy this in the Cloudflare dashboard (Workers & Pages -> Create Worker),
// paste this code in, then go to Settings -> Variables and add an
// encrypted secret named ANTHROPIC_API_KEY with your real key. Never put
// the key in this file or commit it anywhere.
//
// After deploying, you'll get a URL like:
//   https://atlas-nova-proxy.<your-subdomain>.workers.dev
// That's the URL the demo's frontend calls instead of api.anthropic.com.

const ALLOWED_ORIGINS = [
  "https://hire.anuprao.dev",
  "http://localhost:8000", // for local testing only, remove if you don't need it
];

const MAX_TOKENS_CAP = 300;       // hard ceiling, ignores whatever the client asks for
const MAX_HISTORY_TURNS = 8;      // only forward the last N messages, caps cost per request
const MAX_MESSAGE_CHARS = 600;    // reject absurdly long single messages

function corsHeaders(origin) {
  const allowed = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    "Access-Control-Allow-Origin": allowed,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const headers = corsHeaders(origin);

    if (request.method === "OPTIONS") {
      return new Response(null, { headers });
    }

    if (request.method !== "POST") {
      return new Response(JSON.stringify({ error: "method not allowed" }), {
        status: 405,
        headers: { ...headers, "Content-Type": "application/json" },
      });
    }

    if (!ALLOWED_ORIGINS.includes(origin)) {
      return new Response(JSON.stringify({ error: "origin not allowed" }), {
        status: 403,
        headers: { ...headers, "Content-Type": "application/json" },
      });
    }

    let body;
    try {
      body = await request.json();
    } catch (e) {
      return new Response(JSON.stringify({ error: "invalid json" }), {
        status: 400,
        headers: { ...headers, "Content-Type": "application/json" },
      });
    }

    const { system, messages } = body;
    if (!system || !Array.isArray(messages) || messages.length === 0) {
      return new Response(JSON.stringify({ error: "missing system or messages" }), {
        status: 400,
        headers: { ...headers, "Content-Type": "application/json" },
      });
    }

    // Trim history and enforce per-message length caps before it ever
    // reaches Anthropic - this is what keeps a public demo's cost bounded.
    const trimmedMessages = messages.slice(-MAX_HISTORY_TURNS).map((m) => ({
      role: m.role,
      content: String(m.content || "").slice(0, MAX_MESSAGE_CHARS),
    }));

    const anthropicResp = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-6",
        max_tokens: MAX_TOKENS_CAP,
        system,
        messages: trimmedMessages,
      }),
    });

    const data = await anthropicResp.json();

    return new Response(JSON.stringify(data), {
      status: anthropicResp.status,
      headers: { ...headers, "Content-Type": "application/json" },
    });
  },
};
