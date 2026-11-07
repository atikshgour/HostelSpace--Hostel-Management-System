"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Alert, Button, FormField, Loading } from "@/components/ui";

export default function Profile() {
  const router = useRouter();
  const [p, setP] = useState(null);
  const [phone, setPhone] = useState("");
  const [loadError, setLoadError] = useState("");
  const [msg, setMsg] = useState({ type: "", text: "" });
  const [fieldErr, setFieldErr] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api("/api/auth/profile/")
      .then((d) => { setP(d); setPhone(d.phone); })
      .catch((e) => {
        if (e.status === 401) router.replace("/login");
        else setLoadError(e.message || "Could not load your profile. Please try again.");
      });
  }, [router]);

  async function save(e) {
    e.preventDefault();
    setMsg({ type: "", text: "" });
    setFieldErr("");
    setSaving(true);
    try {
      const d = await api("/api/auth/profile/", { method: "PATCH", body: { phone } });
      setP(d);
      setMsg({ type: "success", text: "Phone number updated." });
    } catch (err) {
      setFieldErr(err.fields?.phone || "");
      setMsg({ type: "error", text: err.message || "Could not save. Please try again." });
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="p-8 max-w-lg">
      <a href="/dashboard" className="underline text-sm">← Dashboard</a>
      <h1 className="text-2xl font-bold mt-2">My profile</h1>
      {loadError && <div className="mt-4"><Alert type="error">{loadError}</Alert></div>}
      {!p && !loadError && <Loading text="Loading your profile..." />}
      {p && (
        <>
          <dl className="mt-4 hs-card space-y-2">
            {[["Name", p.name], ["Username", p.username], ["USN", p.usn], ["Room", p.room_number]].map(([k, v]) => (
              <div key={k} className="flex justify-between">
                <dt className="font-medium">{k}</dt>
                <dd style={v ? undefined : { color: "var(--hs-muted)" }}>{v || "Not set"}</dd>
              </div>
            ))}
          </dl>
          <form onSubmit={save} className="mt-6 hs-card space-y-3" noValidate>
            <FormField id="phone" label="Phone number" value={phone} error={fieldErr}
              inputMode="tel" onChange={(e) => setPhone(e.target.value)} />
            <Alert type={msg.type}>{msg.text}</Alert>
            <Button type="submit" loading={saving} loadingText="Saving...">Save phone</Button>
          </form>
        </>
      )}
    </main>
  );
}
