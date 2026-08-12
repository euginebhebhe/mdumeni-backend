/**
 * MDUMENI Backend — Cloudflare Worker
 * 
 * This worker routes requests from Cloudflare to your FastAPI backend.
 * It handles:
 *  - Request validation and forwarding
 *  - CORS headers
 *  - Error handling
 *  - Request/response logging
 */

import { handleRequest } from './index.js';

// ── Cloudflare Worker handler ──────────────────────────────────────────────
export default {
  async fetch(request, env, ctx) {
    return handleRequest(request, env, ctx);
  },

  async scheduled(event, env, ctx) {
    // Handle scheduled events if needed (e.g., periodic tasks)
    console.log('Scheduled event triggered');
  }
};
