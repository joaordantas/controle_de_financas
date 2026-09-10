import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import type { User } from "../types";

const STORAGE_KEY = "controle-financas-user";

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  login: (user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const rawUser = window.localStorage.getItem(STORAGE_KEY);

    if (!rawUser) {
      return null;
    }

    try {
      return JSON.parse(rawUser) as User;
    } catch {
      window.localStorage.removeItem(STORAGE_KEY);
      return null;
    }
  });

  useEffect(() => {
    if (user) {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
      return;
    }

    window.localStorage.removeItem(STORAGE_KEY);
  }, [user]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      login: setUser,
      logout: () => setUser(null),
    }),
    [user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function AppProviders({ children }: { children: ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth precisa ser usado dentro de AppProviders.");
  }

  return context;
}
