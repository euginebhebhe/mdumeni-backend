/**
 * MDUMENI Backend — Request Handler
 * 
 * Routes incoming HTTP requests to the FastAPI backend.
 * Ensures proper headers, CORS, and error handling.
 */

// Default backend URL (override in wrangler.toml with env.BACKEND_URL)
const DEFAULT_BACKEND_URL = 'http://localhost:8000';

/**
 * Main request handler
 * @param {Request} request - Incoming HTTP request
 * @param {Object} env - Cloudflare environment variables
 * @param {Object} ctx - Cloudflare context
 * @returns {Response} HTTP response
 */
export async function handleRequest(request, env, ctx) {
  try {
    // Get backend URL from environment, with fallback
    const backendUrl = env.BACKEND_URL || DEFAULT_BACKEND_URL;
    
    // Parse the incoming request URL
    const url = new URL(request.url);
    
    // Construct the backend URL with the same path and query
    const backendRequestUrl = new URL(url.pathname + url.search, backendUrl);
    
    console.log(`[${request.method}] ${url.pathname} -> ${backendRequestUrl.toString()}`);
    
    // Build headers for the backend request
    const headers = new Headers(request.headers);
    
    // Remove host header (let fetch set it automatically)
    headers.delete('host');
    
    // Preserve original request headers but ensure proper content-type
    if (!headers.has('content-type') && request.method !== 'GET' && request.method !== 'HEAD') {
      headers.set('content-type', 'application/json');
    }
    
    // Forward the request to FastAPI backend
    const backendRequest = new Request(backendRequestUrl, {
      method: request.method,
      headers: headers,
      body: request.body,
    });
    
    // Fetch from backend with timeout
    const response = await Promise.race([
      fetch(backendRequest),
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Backend timeout')), 30000)
      )
    ]);
    
    // Clone response to modify headers
    const responseBody = await response.arrayBuffer();
    const newResponse = new Response(responseBody, response);
    
    // Add CORS headers
    newResponse.headers.set('Access-Control-Allow-Origin', '*');
    newResponse.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    newResponse.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Key');
    newResponse.headers.set('Access-Control-Max-Age', '86400');
    
    // Add security headers
    newResponse.headers.set('X-Content-Type-Options', 'nosniff');
    newResponse.headers.set('X-Frame-Options', 'DENY');
    
    return newResponse;
    
  } catch (error) {
    console.error('Worker error:', error);
    
    // Return error response
    return new Response(
      JSON.stringify({
        error: 'Service unavailable',
        message: error.message,
        timestamp: new Date().toISOString()
      }),
      {
        status: 503,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      }
    );
  }
}

/**
 * Handle OPTIONS requests (CORS preflight)
 */
export async function handleOptions(request) {
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
        'Access-Control-Max-Age': '86400'
      }
    });
  }
}
