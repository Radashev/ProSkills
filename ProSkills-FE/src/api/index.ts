import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { authApi } from "./auth";
import { ROLE_PATHS } from "../routes/paths";
import { GUEST_ROLE } from "../models/User";
import { urls } from "./urls";

interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});

// to prevent infinite loops
let isRefreshing = false;
let failedQueue: {
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}[] = [];

const processQueue = (error: Error | null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve();
    }
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as CustomAxiosRequestConfig;
    const pathname = new URL(originalRequest.url || "", BASE_URL).pathname;
    const currentPath = pathname.startsWith("/")
      ? pathname.substring(1)
      : pathname;
    const guestAccessiblePaths = new Set(ROLE_PATHS[GUEST_ROLE] || []);

    // Get all auth paths including nested ones
    const authPaths = new Set(
      [
        urls.auth.login,
        urls.auth.logout,
        urls.auth.requestPasswordReset,
        urls.auth.resetPassword,
        urls.auth.getToken,
        urls.auth.refreshToken,
        ...Object.values(urls.auth.register).flat(),
      ].map((path) => `auth${path}`)
    );

    // Don't retry for guest paths or auth endpoints
    if (guestAccessiblePaths.has(currentPath) || authPaths.has(currentPath)) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(() => api(originalRequest))
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        await authApi.refreshToken();
        processQueue(null);
        isRefreshing = false;
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(null);
        isRefreshing = false;
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
