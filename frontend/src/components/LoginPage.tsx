"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth";

export const LoginPage = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    // Simulate a small delay for better UX
    setTimeout(() => {
      const success = login(username, password);
      if (success) {
        // Credentials are correct, localStorage updated, and AuthProvider will detect it
        // No need to navigate, just clear the form
        setUsername("");
        setPassword("");
      } else {
        setError("Invalid credentials. Try user / password");
        setPassword("");
      }
      setIsLoading(false);
    }, 300);
  };

  return (
    <div className="relative overflow-hidden">
      <div className="pointer-events-none absolute left-0 top-0 h-[420px] w-[420px] -translate-x-1/3 -translate-y-1/3 rounded-full bg-[radial-gradient(circle,_rgba(32,157,215,0.25)_0%,_rgba(32,157,215,0.05)_55%,_transparent_70%)]" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-[520px] w-[520px] translate-x-1/4 translate-y-1/4 rounded-full bg-[radial-gradient(circle,_rgba(117,57,145,0.18)_0%,_rgba(117,57,145,0.05)_55%,_transparent_75%)]" />

      <main className="relative mx-auto flex min-h-screen max-w-[1500px] flex-col items-center justify-center px-6">
        <div className="w-full max-w-md rounded-[32px] border border-[var(--stroke)] bg-white/80 p-8 shadow-[var(--shadow)] backdrop-blur">
          <div className="mb-8 text-center">
            <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
              Kanban Studio
            </p>
            <h1 className="mt-3 font-display text-3xl font-semibold text-[var(--navy-dark)]">
              Sign In
            </h1>
            <p className="mt-3 text-sm leading-6 text-[var(--gray-text)]">
              Enter your credentials to access your Kanban board
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-[var(--navy-dark)] mb-2">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="user"
                disabled={isLoading}
                className="w-full rounded-xl border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 text-sm placeholder-[var(--gray-text)] focus:border-[var(--primary-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-blue)]/20 disabled:opacity-50"
                data-testid="login-username"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-[var(--navy-dark)] mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="password"
                disabled={isLoading}
                className="w-full rounded-xl border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 text-sm placeholder-[var(--gray-text)] focus:border-[var(--primary-blue)] focus:outline-none focus:ring-2 focus:ring-[var(--primary-blue)]/20 disabled:opacity-50"
                data-testid="login-password"
              />
            </div>

            {error && (
              <div className="rounded-lg bg-red-50 border border-red-200 p-3">
                <p className="text-sm text-red-700" data-testid="login-error">
                  {error}
                </p>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-6 rounded-xl bg-[var(--secondary-purple)] px-6 py-3 text-sm font-semibold text-white hover:bg-[var(--secondary-purple)]/90 disabled:opacity-60 transition-colors"
              data-testid="login-submit"
            >
              {isLoading ? "Signing in..." : "Sign In"}
            </button>

            <div className="mt-4 pt-4 border-t border-[var(--stroke)]">
              <p className="text-xs text-[var(--gray-text)] text-center">
                Demo credentials: <strong>user</strong> / <strong>password</strong>
              </p>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};
