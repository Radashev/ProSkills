import { create } from "zustand";
import { persist } from "zustand/middleware";
import { AuthUser } from "../models/User";
import { authApi } from "../api/auth";

interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  loginAttempts: number;
  setUser: (user: AuthUser | null) => void;
  checkAuth: () => Promise<void>;
  logout: () => Promise<void>;
  incrementLoginAttempts: () => void;
  resetLoginAttempts: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      loginAttempts: 0,

      incrementLoginAttempts: () =>
        set((state) => ({ loginAttempts: state.loginAttempts + 1 })),

      resetLoginAttempts: () => set({ loginAttempts: 0 }),

      setUser: (user) => set({ user, isAuthenticated: !!user }),

      checkAuth: async () => {
        try {
          const { data } = await authApi.getToken();
          set({ user: data, isAuthenticated: true });
        } catch (error: any) {
          if (error.response?.status === 401) {
            try {
              await authApi.refreshToken();
              const { data } = await authApi.getToken();
              set({ user: data, isAuthenticated: true });
            } catch {
              set({ user: null, isAuthenticated: false });
            }
          } else {
            set({ user: null, isAuthenticated: false });
          }
        }
      },

      logout: async () => {
        try {
          await authApi.logout();
        } finally {
          set({ user: null, isAuthenticated: false });
        }
      },
    }),
    {
      name: "auth-storage",
    }
  )
);
