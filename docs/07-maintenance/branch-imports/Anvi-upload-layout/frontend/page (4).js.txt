"use client";
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Alert, Button, EmptyState, FormField, Loading, StatusBadge } from "@/components/ui";

const ROLES = [
  ["student", "Student"], ["warden", "Warden"], ["chief_warden", "Chief Warden"],
  ["director", "Hostel Director"], ["maintenance", "Maintenance Staff"],
  ["mess", "Mess Staff"], ["laundry", "Laundry Staff"],
];
const EMPTY = { username: "", name: "", role: "student", password: "" };

export default function DirectorUsers() {
  const router = useRouter();
  const [users, setUsers] = useState(null);
  const [loadError, setLoadError] = useState("");
  const [form, setForm] = useState(EMPTY);
  const [fields, setFields] = useState({});
  const [msg, setMsg] = useState({ type: "", text: "" });
  const [saving, setSaving] = useState(false);

  const load = useCallback(() => {
    api("/api/auth/users/")
      .then((d) => setUsers(d.users))
      .catch((e) => {
        if (e.status === 401) router.replace("/login");
        else setLoadError(e.message || "Could not load users. Please try again.");
      });
  }, [router]);

  useEffect(load, [load]);

  async function create(e) {
    e.preventDefault();
    setMsg({ type: "", text: "" });
    setFields({});
    setSaving(true);
    try {
      await api("/api/auth/users/", { method: "POST", body: form });
      setForm(EMPTY);
      setMsg({ type: "success", text: "User created." });
      load();
    } catch (err) {
      setFields(err.fields || {});
      setMsg({ type: "error", text: err.message || "Could not create user." });
    } finally {
      setSaving(false);
    }
  }

  async function update(id, body) {
    setMsg({ type: "", text: "" });
    try {
      await api(`/api/auth/users/${id}/`, { method: "PATCH", body });
      setMsg({ type: "success", text: "User updated." });
      load();
    } catch (err) {
      setMsg({ type: "error", text: err.message || "Could not update user." });
    }
  }

  if (loadError) return <main className="p-8"><Alert type="error">{loadError}</Alert></main>;
  if (!users) return <main className="p-8"><Loading text="Loading users..." /></main>;

  return (
    <main className="p-8 max-w-4xl space-y-6">
      <div>
        <a href="/dashboard" className="underline text-sm">← Dashboard</a>
        <h1 className="text-2xl font-bold mt-2">Users & roles</h1>
      </div>
      <Alert type={msg.type}>{msg.text}</Alert>

      <form onSubmit={create} className="hs-card space-y-3" noValidate>
        <h2 className="font-semibold">Add user</h2>
        <FormField id="username" label="Username" value={form.username} error={fields.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })} />
        <FormField id="name" label="Full name" value={form.name} error={fields.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <div>
          <label htmlFor="role" className="hs-label">Role</label>
          <select id="role" className="hs-input" value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value })}>
            {ROLES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
          {fields.role && <p className="hs-field-error">{fields.role}</p>}
        </div>
        <FormField id="password" label="Temporary password" type="password" value={form.password}
          error={fields.password} autoComplete="new-password"
          onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <Button type="submit" loading={saving} loadingText="Creating...">Create user</Button>
      </form>

      {users.length === 0 ? (
        <EmptyState title="No users yet" message="Create the first user above." />
      ) : (
        <div className="hs-card overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr><th className="p-2">Username</th><th className="p-2">Name</th>
                <th className="p-2">Role</th><th className="p-2">Status</th><th className="p-2"></th></tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-t">
                  <td className="p-2">{u.username}</td>
                  <td className="p-2">{u.name}</td>
                  <td className="p-2">
                    <select aria-label={`Role for ${u.username}`} className="hs-input" value={u.role}
                      onChange={(e) => update(u.id, { role: e.target.value })}>
                      {ROLES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                    </select>
                  </td>
                  <td className="p-2">
                    <StatusBadge status={u.is_active ? "Active" : "Inactive"} tone={u.is_active ? "ok" : "bad"} />
                  </td>
                  <td className="p-2">
                    <Button variant="secondary" onClick={() => update(u.id, { is_active: !u.is_active })}>
                      {u.is_active ? "Deactivate" : "Reactivate"}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
