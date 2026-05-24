// Prevent Next.js from prerendering this page during build.
export const dynamic = "force-dynamic";

// Import the client wrapper directly; it's a client component so it will be
// rendered on the client and not execute server‑side hooks during prerender.
import AuthWrapper from "./AuthWrapper";

export default function Home() {
  return <AuthWrapper />;
}
