"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";

const KanbanBoard = dynamic(() => import("@/components/KanbanBoard").then(mod => ({ default: mod.KanbanBoard })), {
  ssr: false,
  loading: () => <div className="flex min-h-screen items-center justify-center"><p className="text-gray-500">Loading board...</p></div>,
});

export const ProtectedBoard = () => {
  const { isAuthenticated, logout } = useAuth();
  const router = useRouter();
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    setIsHydrated(true);
  }, []);

  useEffect(() => {
    if (isHydrated && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, isHydrated, router]);

  if (!isHydrated) {
    return <div className="flex min-h-screen items-center justify-center"><p className="text-gray-500">Initializing...</p></div>;
  }

  if (!isAuthenticated) {
    return <div className="flex min-h-screen items-center justify-center"><p className="text-gray-500">Redirecting to login...</p></div>;
  }

  return (
    <div className="relative">
      <div className="absolute top-4 right-6 z-50">
        <button
          onClick={() => {
            logout();
            router.push("/login");
          }}
          className="rounded-lg bg-gray-200 hover:bg-gray-300 px-4 py-2 text-sm font-semibold text-[var(--navy-dark)] transition-colors"
          data-testid="logout-button"
        >
          Logout
        </button>
      </div>
      <KanbanBoard />
    </div>
  );
};
