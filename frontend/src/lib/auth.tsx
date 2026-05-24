"use client";

import { createContext, useContext, useState, useEffect } from "react";

interface AuthContextType {
  isAuthenticated: boolean;
  login: (username: string, password: string) => boolean;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    // Load auth state from localStorage after hydration
    const stored = localStorage.getItem("auth_token");
    setIsAuthenticated(!!stored);
    setIsHydrated(true);
  }, []);

  const login = (username: string, password: string): boolean => {
    // Hardcoded credentials for MVP
    if (username === "user" && password === "password") {
      localStorage.setItem("auth_token", "true");
      setIsAuthenticated(true);
      return true;
    }
    return false;
  };

  const logout = () => {
    localStorage.removeItem("auth_token");
    setIsAuthenticated(false);
  };

  if (!isHydrated) {
    return <>{children}</>;
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    // When used outside of an AuthProvider (e.g., during server rendering),
    // return a safe default rather than throwing. This prevents build/runtime
    // errors where client hooks may be referenced in server contexts.
    return {
      isAuthenticated: false,
      login: () => false,
      logout: () => {},
    } as AuthContextType;
  }
  return context;
}
