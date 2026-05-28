/**
 * API Configuration
 * 
 * Supports environment variables configured in Vercel/Vite:
 * - VITE_API_BASE_URL: The HTTP URL of the FastAPI backend (e.g., https://username-space.hf.space)
 * - VITE_WS_URL: The WebSocket URL of the FastAPI backend (e.g., wss://username-space.hf.space)
 */

// Base URL for HTTP API calls (default to localhost:8000 in dev)
export const API_BASE = import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? "http://localhost:8000" : "");

// Constructs the full WebSocket URL for the given session ID
export function getWsUrl(sessionId) {
  const envWsUrl = import.meta.env.VITE_WS_URL;
  
  if (envWsUrl) {
    // Strip trailing slash if present
    const cleanedBase = envWsUrl.endsWith('/') ? envWsUrl.slice(0, -1) : envWsUrl;
    // Check if it already includes protocol, if not prepend wss://
    const baseWithProtocol = cleanedBase.startsWith('ws') ? cleanedBase : `wss://${cleanedBase}`;
    return `${baseWithProtocol}/ws/${sessionId}`;
  }
  
  // Fallback / Auto-detection (Standard HTTP/HTTPS translation)
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  
  // If API_BASE is absolute (e.g., started with http), translate it to ws protocol
  if (API_BASE.startsWith('http')) {
    const wsHost = API_BASE.replace(/^https?:\/\//, '');
    const wsProtocol = API_BASE.startsWith('https') ? 'wss:' : 'ws:';
    return `${wsProtocol}//${wsHost}/ws/${sessionId}`;
  }
  
  // Ultimate local dev / standard fallback
  const host = import.meta.env.DEV ? "localhost:8000" : window.location.host;
  return `${protocol}//${host}/ws/${sessionId}`;
}
