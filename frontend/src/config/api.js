/**
 * API Configuration
 * 
 * In production (Docker/HF Spaces), the frontend is served by the backend
 * on the same origin, so we use relative paths.
 * In development, Vite proxies /api/* to the backend at localhost:8000.
 */

// Base URL for HTTP API calls
export const API_BASE = import.meta.env.DEV ? "http://localhost:8000" : "";

// WebSocket host (just host:port, no protocol)
export function getWsHost() {
  if (import.meta.env.DEV) {
    return "localhost:8000";
  }
  // In production, use the current page's host
  return window.location.host;
}
