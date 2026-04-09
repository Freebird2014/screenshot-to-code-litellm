import { create } from "zustand";
import { persist } from "zustand/middleware";
import { HTTP_BACKEND_URL } from "../config";

// Auth store interface
interface AuthStore {
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (password: string) => Promise<boolean>;
  logout: () => void;
  clearError: () => void;
  getAuthHeaders: () => Record<string, string>;
  verifyToken: () => Promise<boolean>;
}

interface LoginResponse {
  token: string;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (password: string): Promise<boolean> => {
        set({ isLoading: true, error: null });

        try {
          const response = await fetch(`${HTTP_BACKEND_URL}/api/login`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ password }),
          });

          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || "Invalid password");
          }

          const data: LoginResponse = await response.json();
          set({
            token: data.token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          return true;
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : "Login failed",
          });
          return false;
        }
      },

      logout: () => {
        set({
          token: null,
          isAuthenticated: false,
          error: null,
        });
      },

      clearError: () => {
        set({ error: null });
      },

      getAuthHeaders: (): Record<string, string> => {
        const { token } = get();
        if (!token) {
          return {} as Record<string, string>;
        }
        return {
          Authorization: `Bearer ${token}`,
        };
      },

      verifyToken: async (): Promise<boolean> => {
        const { token, logout } = get();
        if (!token) {
          return false;
        }

        try {
          const response = await fetch(`${HTTP_BACKEND_URL}/api/verify-token`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });

          if (!response.ok) {
            // Token is invalid, clear auth state
            logout();
            return false;
          }

          return true;
        } catch (error) {
          // Network error or other issue, don't clear auth state
          // just return false to indicate verification failed
          console.error("Token verification failed:", error);
          return false;
        }
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({ token: state.token, isAuthenticated: state.isAuthenticated }),
    }
  )
);
