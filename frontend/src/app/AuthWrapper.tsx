"use client";

import dynamicImport from "next/dynamic";
import { AuthProvider, useAuth } from "@/lib/auth";
import { useEffect, useState } from "react";

// Dynamically load heavy components without SSR.
const LoginPage = dynamicImport(
  () => import("@/components/LoginPage").then((mod) => ({ default: mod.LoginPage })),
  {
    ssr: false,
    loading: () => (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-500">Loading...</p>
      </div>
    ),
  },
);

const ProtectedBoard = dynamicImport(
  () => import("@/components/ProtectedBoard").then((mod) => ({ default: mod.ProtectedBoard })),
  {
    ssr: false,
    loading: () => (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-500">Loading...</p>
      </div>
    ),
  },
);

// Separate component that consumes the auth context.
function AuthContent() {
  const { isAuthenticated } = useAuth();
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    setIsHydrated(true);
  }, []);

  if (!isHydrated) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  return isAuthenticated ? <ProtectedBoard /> : <LoginPage />;
}

export default function AuthWrapper() {
  // Wrap the auth context around the content component.
  return (
    <AuthProvider>
      <AuthContent />
    </AuthProvider>
  );
}
