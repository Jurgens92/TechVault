import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

// Use VITE_API_URL if explicitly set, otherwise use current origin (for production deployments)
// This allows the app to work with any domain/IP without rebuilding
const API_URL = import.meta.env.VITE_API_URL !== undefined && import.meta.env.VITE_API_URL !== ''
  ? import.meta.env.VITE_API_URL
  : (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000');

// Authentication uses HttpOnly cookies set by the server at login. JavaScript never
// sees the tokens, so they cannot be stolen by injected script. Because the browser
// attaches the cookies automatically, state-changing requests also carry a CSRF
// token (read from the csrftoken cookie and echoed in the X-CSRFToken header).
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  withXSRFToken: true,
});

// Older versions kept tokens in localStorage. Remove any that are still there.
const clearLegacyTokens = (): void => {
  try {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  } catch {
    // storage unavailable - nothing to clean up
  }
};
clearLegacyTokens();

const PUBLIC_PATHS = ['/login'];

const redirectToLogin = (): void => {
  if (!PUBLIC_PATHS.some((p) => window.location.pathname.startsWith(p))) {
    window.location.href = '/login';
  }
};

// Only one refresh may run at a time: refresh tokens are single-use (rotated and
// revoked on use), so parallel 401s must all wait for the same refresh call.
let refreshInFlight: Promise<void> | null = null;

const refreshSession = (): Promise<void> => {
  if (!refreshInFlight) {
    refreshInFlight = axios
      .post(`${API_URL}/api/token/refresh/`, {}, { withCredentials: true })
      .then(() => undefined)
      .finally(() => {
        refreshInFlight = null;
      });
  }
  return refreshInFlight;
};

// Requests that must never trigger a refresh-and-retry
const isAuthEndpoint = (url?: string): boolean =>
  !!url && (
    url.includes('/api/token/refresh/') ||
    url.includes('/api/auth/login/') ||
    url.includes('/api/auth/logout/')
  );

// Response interceptor: on 401, refresh the session once and retry the request
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as (InternalAxiosRequestConfig & {
      _retry?: boolean;
      skipAuthRedirect?: boolean;
    }) | undefined;

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !isAuthEndpoint(originalRequest.url)
    ) {
      originalRequest._retry = true;
      try {
        await refreshSession();
        return api(originalRequest);
      } catch (refreshError) {
        // Session is over (refresh token missing, expired or revoked)
        if (!originalRequest.skipAuthRedirect) {
          redirectToLogin();
        }
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

export { api };
export default api;
