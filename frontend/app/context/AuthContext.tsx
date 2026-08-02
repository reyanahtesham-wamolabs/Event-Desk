import React, { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import { api, setTokens, clearTokens, type User } from "../lib/api";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string, role: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const me = await api.get<User>("/users/me");
      setUser(me);
    } catch {
      setUser(null);
      clearTokens();
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      refresh();
    } else {
      setLoading(false);
    }
  }, [refresh]);

  const login = async (email: string, password: string) => {
    const data = await api.post<{ access_token: string; refresh_token?: string }>("/auth/login", { email, password });
    setTokens(data.access_token, data.refresh_token ?? "");
    const me = await api.get<User>("/users/me");
    setUser(me);
  };

  const signup = async (name: string, email: string, password: string, role: string) => {
    await api.post("/auth/signup", { name, email, password, role });
    await login(email, password);
  };

  const logout = async () => {
    try { await api.post("/auth/logout"); } catch { /* ignore */ }
    clearTokens();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
