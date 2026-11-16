/* Owner: Anvi Srinivas | US-01 | Dev sprint 1 | SRS sprint 1 | Reviewer: Arin Singh (pending) */
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { ErrorMessage } from "@/components/ui/AppShell";
import FormField from "@/components/ui/FormField";
import Button from "@/components/ui/Button";
export default function LoginForm() {
  const router = useRouter();
  const [error, setError] = useState(null),
    [busy, setBusy] = useState(false);
  async function submit(e) {
    e.preventDefault();
    const body = Object.fromEntries(new FormData(e.currentTarget));
    setBusy(true);
    setError(null);
    try {
      await api("/api/auth/login/", { method: "POST", body });
      router.replace("/dashboard");
      router.refresh();
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="hs-login">
      <section className="hs-card">
        <div
          className="hs-brand"
          style={{ justifyContent: "center", marginBottom: 28 }}
        >
          <span className="hs-logo">H</span>HostelSpace
        </div>
        <h1>Welcome back</h1>
        <p className="hs-muted">Sign in to your hostel portal.</p>
        <form method="post" onSubmit={submit}>
          <FormField
            label="Username"
            name="username"
            autoComplete="username"
            required
          />
          <FormField
            label="Password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
          />
          <ErrorMessage error={error} />
          <Button variant="primary" disabled={busy}>
            {busy ? "Signing in…" : "Sign in"}
          </Button>
        </form>
        <p className="hs-muted" style={{ fontSize: 12, marginTop: 24 }}>
          Access is restricted to accounts created by the hostel administration.
        </p>
      </section>
    </main>
  );
}
