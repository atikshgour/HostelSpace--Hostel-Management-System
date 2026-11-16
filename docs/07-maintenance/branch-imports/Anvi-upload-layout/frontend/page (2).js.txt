"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Alert, Button, FormField } from "@/components/ui";

export default function Login() {
  const router = useRouter();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [fields, setFields] = useState({});
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setFields({});
    setLoading(true);
    try {
      await api("/api/auth/login/", { method: "POST", body: form });
      router.replace("/dashboard");
    } catch (err) {
      setError(err.message || "Could not reach the server. Check your connection and try again.");
      setFields(err.fields || {});
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <form onSubmit={submit} className="hs-card p-8 w-full max-w-sm space-y-4" noValidate>
        <h1 className="text-2xl font-bold">HostelSpace Sign in</h1>
        <Alert type="error">{error}</Alert>
        <FormField id="username" label="Username" value={form.username} error={fields.username}
          autoComplete="username"
          onChange={(e) => setForm({ ...form, username: e.target.value })} />
        <FormField id="password" label="Password" type="password" value={form.password}
          error={fields.password} autoComplete="current-password"
          onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <Button type="submit" loading={loading} loadingText="Signing in..." style={{ width: "100%" }}>
          Sign in
        </Button>
      </form>
    </main>
  );
}
