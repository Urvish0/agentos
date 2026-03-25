/**
 * AgentOS Dashboard — Server-Side API Proxy
 *
 * This catch-all route handler proxies all /api/* requests to the backend
 * server-side, so the internal Docker hostname (e.g. agentos_api) is never
 * exposed to the client's browser.
 *
 * This replaces the previous NextResponse.rewrite() approach in middleware.ts
 * which didn't work in Docker because rewrite() for external origins sends a
 * 308 redirect to the client, leaking the internal Docker hostname.
 */

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

async function proxyRequest(request: Request) {
  const url = new URL(request.url);

  // Strip the /api prefix to get the backend path
  const backendPath = url.pathname.replace(/^\/api/, "");
  const proxyUrl = `${BACKEND_URL}${backendPath}${url.search}`;

  // Forward the request headers, excluding host-specific ones
  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("connection");

  const init: RequestInit = {
    method: request.method,
    headers,
  };

  // Forward the body for non-GET/HEAD methods
  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = await request.text();
  }

  try {
    const backendResponse = await fetch(proxyUrl, init);

    // Create the proxied response
    const responseHeaders = new Headers(backendResponse.headers);
    // Remove transfer-encoding as Next.js handles this
    responseHeaders.delete("transfer-encoding");

    return new Response(backendResponse.body, {
      status: backendResponse.status,
      statusText: backendResponse.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error(`[API Proxy] Failed to reach backend at ${proxyUrl}:`, error);
    return new Response(
      JSON.stringify({
        error: "Backend Unavailable",
        detail: `Could not connect to backend at ${BACKEND_URL}. Make sure the AgentOS API server is running.`,
      }),
      {
        status: 502,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}

export async function GET(request: Request) {
  return proxyRequest(request);
}

export async function POST(request: Request) {
  return proxyRequest(request);
}

export async function PUT(request: Request) {
  return proxyRequest(request);
}

export async function PATCH(request: Request) {
  return proxyRequest(request);
}

export async function DELETE(request: Request) {
  return proxyRequest(request);
}
