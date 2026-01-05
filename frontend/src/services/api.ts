import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { AuthTokens } from '@/types/auth';

// Use VITE_API_URL if explicitly set, otherwise use current origin (for production deployments)
// This allows the app to work with any domain/IP without rebuilding
const API_URL = import.meta.env.VITE_API_URL !== undefined && import.meta.env.VITE_API_URL !== ''
  ? import.meta.env.VITE_API_URL
  : (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000');

// Create axios instance with credentials support for HttpOnly cookies
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Security: Enable credentials to allow HttpOnly cookie authentication
  withCredentials: true,
});

// Token management - Uses HttpOnly cookies primarily, with localStorage as fallback
// Note: With HttpOnly cookies, the browser handles token storage automatically
// We keep localStorage methods for backwards compatibility during transition

const getAccessToken = (): string | null => {
  // With HttpOnly cookies, we can't access tokens directly
  // This is kept for backwards compatibility but cookies take precedence
  return localStorage.getItem('access_token');
};

const getRefreshToken = (): string | null => {
  return localStorage.getItem('refresh_token');
};

const setTokens = (tokens: AuthTokens): void => {
  // Store tokens in localStorage as fallback (when backend returns them in response)
  // HttpOnly cookies are set automatically by the browser from Set-Cookie headers
  if (tokens.access) {
    localStorage.setItem('access_token', tokens.access);
  }
  if (tokens.refresh) {
    localStorage.setItem('refresh_token', tokens.refresh);
  }
};

const clearTokens = (): void => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  // Note: HttpOnly cookies are cleared by the logout endpoint via Set-Cookie header
};

// Request interceptor to add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Don't attempt to refresh if the request itself was a token refresh (prevent infinite loop)
    const isRefreshRequest = originalRequest.url?.includes('/api/token/refresh/');

    // If error is 401 and we haven't retried yet and it's not the refresh endpoint
    if (error.response?.status === 401 && !originalRequest._retry && !isRefreshRequest) {
      originalRequest._retry = true;

      try {
        const refreshToken = getRefreshToken();

        if (!refreshToken) {
          clearTokens();
          // Only redirect if not already on login page
          if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login';
          }
          return Promise.reject(error);
        }

        // Try to refresh the token
        const response = await axios.post(`${API_URL}/api/token/refresh/`, {
          refresh: refreshToken,
        });

        // Handle both response formats (access_token/refresh_token or access/refresh)
        const { access, refresh, access_token, refresh_token } = response.data;
        const newAccessToken = access_token || access;
        const newRefreshToken = refresh_token || refresh;

        if (!newAccessToken || !newRefreshToken) {
          console.error('Token refresh failed: Invalid response format', response.data);
          clearTokens();
          // Only redirect if not already on login page
          if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login';
          }
          return Promise.reject(error);
        }

        setTokens({ access: newAccessToken, refresh: newRefreshToken });

        // Retry the original request with new token
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        console.error('Token refresh failed:', refreshError);
        clearTokens();
        // Only redirect if not already on login page
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export { api, setTokens, clearTokens, getAccessToken, getRefreshToken };
export default api;
