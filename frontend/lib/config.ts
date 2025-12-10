/**
 * Application configuration
 * Environment variables are injected at build time from Vercel dashboard
 */

// Backend API URL - set in Vercel environment variables
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// WebSocket URL
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

// Export as default config object
export const config = {
  apiUrl: API_URL,
  wsUrl: WS_URL,
} as const;
