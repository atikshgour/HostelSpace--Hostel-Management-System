"use client";
import { useState } from "react";
import { api } from "@/lib/api";
import { roleLabel } from "@/lib/roles";
import {
  useResource,
  useIdentity,
  ErrorMessage,
  ResourceForm,
} from "@/components/ui/AppShell";
import PageHeader from "@/components/ui/PageHeader";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import StatusBadge from "@/components/ui/StatusBadge";
import DataTable from "@/components/ui/DataTable";
import Dialog from "@/components/ui/Dialog";
const serviceRoles = [
  "STUDENT",
  "LAUNDRY_STAFF",
  "MAINTENANCE_STAFF",
  "MESS_STAFF",
  "CONTENT_STAFF",
  "WARDEN",
  "CHIEF_WARDEN",
  "DIRECTOR",
];
export default function UserManagement() {
  const me = useIdentity(),
    director = me.role === "DIRECTOR";
  const { data, error, refresh } = useResource(["/api/director/users/"]);
  const [editing, setEditing] = useState(null),
    [open, setOpen] = useState(false),
    [kind, setKind] = useState("STUDENT"),
    [query, setQuery] = useState(""),
    [filter, setFilter] = useState("All"),
    [notice, setNotice] = useState("");
  const users = data?.[0] || [],
    isStudent = kind === "STUDENT";
  function edit(u) {
    setEditing(u);
    setKind(u.role);
    setOpen(true);
  }
  const fields = [
    { name: "username", label: "Username" },
    { name: "first_name", label: "First name" },
    { name: "last_name", label: "Last name", optional: true },
    { name: "email", label: "Email address", type: "email", optional: true },
    {
      name: "password",
      label: editing
        ? "New password (leave blank to keep)"
        : "Initial password",
      type: "password",
      optional: !!editing,
    },
    ...(isStudent
      ? [
          { name: "srn", label: "Student number / SRN" },
          { name: "room", label: "Room number" },
          { name: "hostel", label: "Hostel block" },
          ...(director
            ? [
                {
                  name: "assigned_warden",
                  label: "Assigned Warden",
                  options: users
                    .filter((u) => u.role === "WARDEN" && u.is_active)
                    .map((u) => ({ value: u.id, label: u.name })),
                },
              ]
            : []),
        ]
      : []),
    ...(director && kind === "WARDEN"
      ? [
          {
            name: "chief_warden",
            label: "Supervising Chief Warden",
            optional: true,
            nullable: true,
            options: users
              .filter((u) => u.role === "CHIEF_WARDEN" && u.is_active)
              .map((u) => ({ value: u.id, label: u.name })),
          },
        ]
      : []),
    { name: "is_active", label: "Account active", type: "checkbox" },
  ];
  const rows = users.filter(
    (u) =>
      (filter === "All" || u.role === filter) &&
      `${u.name} ${u.username} ${u.profile?.srn || ""}`
        .toLowerCase()
        .includes(query.toLowerCase()),
  );
  return (
    <>
      <PageHeader
        title="People & accounts"
        description={
          director
            ? "Create and maintain authorized accounts and student assignments."
            : "Account oversight. The Director manages authorized accounts and assignments."
        }
      >
        {director ? (
          <Button
            variant="primary"
            onClick={() => {
              setEditing(null);
              setKind("STUDENT");
              setOpen(true);
            }}
          >
            + Create account
          </Button>
        ) : null}
      </PageHeader>
      <ErrorMessage error={error} />
      {notice ? (
        <p className="hs-success" role="status">
          {notice}
        </p>
      ) : null}
      <div className="hs-toolbar">
        <label>
          Search people
          <input
            type="search"
            placeholder="Name, username or student number"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </label>
        <label>
          Account type
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option>All</option>
            {[...new Set(users.map((u) => u.role))].map((r) => (
              <option key={r} value={r}>
                {roleLabel(r)}
              </option>
            ))}
          </select>
        </label>
        <span className="hs-muted">{rows.length} accounts</span>
      </div>
      <Card>
        <DataTable
          headers={[
            "Person",
            "Account type",
            "Room / hostel",
            "Status",
            "Action",
          ]}
          rows={rows.map((u) => [
            <span key="name">
              <strong>{u.name}</strong>
              <small className="hs-cell-sub">
                {u.username}
                {u.profile?.srn ? ` · ${u.profile.srn}` : ""}
              </small>
            </span>,
            roleLabel(u.role),
            u.profile
              ? `${u.profile.hostel} · ${u.profile.room}`
              : "Service team",
            <StatusBadge key="active">
              {u.is_active ? "Active" : "Inactive"}
            </StatusBadge>,
            <Button key="edit" onClick={() => edit(u)}>
              Edit account
            </Button>,
          ])}
        />
        {data && !rows.length ? (
          <p className="hs-empty">
            No matching accounts. Try a different search.
          </p>
        ) : null}
      </Card>
      {open ? (
        <Dialog
          className="hs-account-dialog"
          title={editing ? `Edit ${editing.name}` : "Create an account"}
          onClose={() => setOpen(false)}
        >
          {!editing ? (
            <label className="hs-field">
              Account type
              <select value={kind} onChange={(e) => setKind(e.target.value)}>
                {serviceRoles.map((r) => (
                  <option key={r} value={r}>
                    {roleLabel(r)}
                  </option>
                ))}
              </select>
            </label>
          ) : null}
          <p className="hs-muted">
            {isStudent
              ? "Enter the student’s room and student number. Laundry groups are calculated automatically."
              : "Service staff receive only the permissions for their account type."}{" "}
            Use a strong, unique initial password and share it privately.
          </p>
          <ResourceForm
            key={`${editing?.id || "new"}-${kind}`}
            title={isStudent ? "Student details" : "Account details"}
            fields={fields}
            initial={
              editing
                ? { ...editing, ...editing.profile }
                : { is_active: true, hostel: "Block A" }
            }
            button={editing ? "Save changes" : "Create account"}
            onSave={async (body) => {
              await api(
                `/api/director/users/${editing ? editing.id + "/" : ""}`,
                {
                  method: editing ? "PATCH" : "POST",
                  body: { ...body, role: kind },
                },
              );
              setNotice(
                editing
                  ? "Account updated."
                  : "Account created. Share the initial password privately.",
              );
              setOpen(false);
              refresh();
            }}
          />
        </Dialog>
      ) : null}
    </>
  );
}
