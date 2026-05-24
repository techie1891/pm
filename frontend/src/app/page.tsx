// Server component – force dynamic rendering to avoid prerendering.
export const dynamic = "force-dynamic";
// Disable ISR/static generation for this page.
export const revalidate = false;

import AuthWrapper from "./AuthWrapper";

export default function Home() {
  // Delegate auth handling to a client‑side wrapper.
  return <AuthWrapper />;
}
