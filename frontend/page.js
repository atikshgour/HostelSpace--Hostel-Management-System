"use client";
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Alert, Button, EmptyState, FormField, Loading, StatusBadge } from "@/components/ui";

const STAFF = ["warden", "chief_warden", "director"];

// Field config per content type (mirrors backend validation).
const TYPES = {
  notices: { label: "Notices", fields: [["title", "Title"], ["body", "Details", "textarea"]], heading: "title" },
  contacts: { label: "Contacts", fields: [["name", "Name"], ["designation", "Designation"], ["phone", "Phone"], ["email", "Email (optional)"]], heading: "name" },
  rules: { label: "Rules", fields: [["title", "Title"], ["body", "Details", "textarea"], ["order", "Display order (0 = first)", "number"]], heading: "title" },
};

function blank(kind) {
  return Object.fromEntries(TYPES[kind].fields.map(([k, , t]) => [k, t === "number" ? "0" : ""]));
}

export default function ContentPage() {
  const router = useRouter();
  const [me, setMe] = useState(null);
  const [kind, setKind] = useState("notices");
  const [items, setItems] = useState(null);
  const [loadError, setLoadError] = useState("");
  const [form, setForm] = useState(blank("notices"));
  const [editId, setEditId] = useState(null);
  const [fields, setFields] = useState({});
  const [msg, setMsg] = useState({ type: "", text: "" });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api("/api/auth/me/").then(setMe).catch(() => router.replace("/login"));
  }, [router]);

  const load = useCallback(() => {
    setItems(null);
    setLoadError("");
    api(`/api/content/${kind}/`)
      .then((d) => setItems(d.items))
      .catch((e) => setLoadError(e.message || "Could not load this list. Please try again."));
  }, [kind]);

  useEffect(() => { if (me) load(); }, [me, load]);

  function switchKind(k) {
    setKind(k); setForm(blank(k)); setEditId(null); setFields({}); setMsg({ type: "", text: "" });
  }

  function startEdit(it) {
    setEditId(it.id);
    setForm(Object.fromEntries(TYPES[kind].fields.map(([k]) => [k, String(it[k] ?? "")])));
    setFields({}); setMsg({ type: "", text: "" });
  }

  async function save(e) {
    e.preventDefault();
    setSaving(true); setFields({}); setMsg({ type: "", text: "" });
    const body = { ...form };
    if (kind === "rules") body.order = Number(form.order);
    try {
      if (editId) await api(`/api/content/${kind}/${editId}/`, { method: "PATCH", body });
      else await api(`/api/content/${kind}/`, { method: "POST", body });
      setMsg({ type: "success", text: editId ? "Saved." : "Added." });
      setForm(blank(kind)); setEditId(null);
      load();
    } catch (err) {
      setFields(err.fields || {});
      setMsg({ type: "error", text: err.message || "Could not save. Please try again." });
    } finally {
      setSaving(false);
    }
  }

  async function toggle(it) {
    setMsg({ type: "", text: "" });
    try {
      await api(`/api/content/${kind}/${it.id}/`, { method: "PATCH", body: { is_active: !it.is_active } });
      load();
    } catch (err) {
      setMsg({ type: "error", text: err.message || "Could not update. Please try again." });
    }
  }

  if (!me) return <main className="p-8"><Loading /></main>;
  const staff = STAFF.includes(me.role);
  const cfg = TYPES[kind];

  return (
    <main className="p-8 max-w-3xl space-y-6">
      <div>
        <a href="/dashboard" className="underline text-sm">← Dashboard</a>
        <h1 className="text-2xl font-bold mt-2">Notices, contacts & rules</h1>
      </div>

      <div className="flex gap-2" role="tablist">
        {Object.entries(TYPES).map(([k, t]) => (
          <Button key={k} role="tab" aria-selected={k === kind}
            variant={k === kind ? "primary" : "secondary"} onClick={() => switchKind(k)}>
            {t.label}
          </Button>
        ))}
      </div>

      <Alert type={msg.type}>{msg.text}</Alert>

      {staff && (
        <form onSubmit={save} className="hs-card space-y-3" noValidate>
          <h2 className="font-semibold">{editId ? `Edit ${cfg.label.slice(0, -1).toLowerCase()}` : `Add to ${cfg.label.toLowerCase()}`}</h2>
          {cfg.fields.map(([k, label, type]) =>
            type === "textarea" ? (
              <div key={k}>
                <label htmlFor={k} className="hs-label">{label}</label>
                <textarea id={k} rows={4} className="hs-input" value={form[k]}
                  aria-invalid={fields[k] ? "true" : "false"}
                  onChange={(e) => setForm({ ...form, [k]: e.target.value })} />
                {fields[k] && <p className="hs-field-error">{fields[k]}</p>}
              </div>
            ) : (
              <FormField key={k} id={k} label={label} type={type === "number" ? "number" : "text"}
                value={form[k]} error={fields[k]}
                onChange={(e) => setForm({ ...form, [k]: e.target.value })} />
            )
          )}
          <div className="flex gap-2">
            <Button type="submit" loading={saving} loadingText="Saving...">{editId ? "Save changes" : "Add"}</Button>
            {editId && <Button type="button" variant="secondary" onClick={() => switchKind(kind)}>Cancel</Button>}
          </div>
        </form>
      )}

      {loadError && <Alert type="error">{loadError}</Alert>}
      {!items && !loadError && <Loading text={`Loading ${cfg.label.toLowerCase()}...`} />}
      {items && items.length === 0 && (
        <EmptyState title={`No ${cfg.label.toLowerCase()} yet`}
          message={staff ? "Use the form above to add the first one." : "Nothing has been published yet. Check back later."} />
      )}
      {items && items.length > 0 && (
        <ul className="space-y-3">
          {items.map((it) => (
            <li key={it.id} className="hs-card">
              <div className="flex justify-between items-start gap-2">
                <h3 className="font-semibold">{it[cfg.heading]}</h3>
                {staff && <StatusBadge status={it.is_active ? "Active" : "Inactive"} tone={it.is_active ? "ok" : "bad"} />}
              </div>
              {kind === "contacts" ? (
                <p className="mt-1">{it.designation} · {it.phone}{it.email ? ` · ${it.email}` : ""}</p>
              ) : (
                <p className="mt-1 whitespace-pre-wrap">{it.body}</p>
              )}
              {staff && (
                <div className="mt-3 flex gap-2">
                  <Button variant="secondary" onClick={() => startEdit(it)}>Edit</Button>
                  <Button variant="secondary" onClick={() => toggle(it)}>
                    {it.is_active ? "Deactivate" : "Reactivate"}
                  </Button>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
