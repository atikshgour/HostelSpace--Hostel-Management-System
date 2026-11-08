"use client";
import Link from "next/link";
import { useState } from "react";
import {
  useResource,
  useIdentity,
  ErrorMessage,
  ResourceForm,
} from "@/components/ui/AppShell";
import Card from "@/components/ui/Card";
import PageHeader from "@/components/ui/PageHeader";
import Button from "@/components/ui/Button";
import StatusBadge from "@/components/ui/StatusBadge";
import HistoryTimeline from "@/components/ui/HistoryTimeline";
import { api } from "@/lib/api";
import { dateTime } from "@/lib/format";
import Dialog from "@/components/ui/Dialog";
import DataTable from "@/components/ui/DataTable";
export function ComplaintForm({ onSaved }) {
  return (
    <Card>
      <ResourceForm
        title="New maintenance complaint"
        fields={[
          {
            name: "category",
            label: "Category",
            options: [
              "Electrical",
              "Plumbing",
              "Furniture",
              "Cleaning",
              "Other",
            ],
          },
          { name: "description", label: "Description", type: "textarea" },
        ]}
        button="Submit complaint"
        onSave={async (body) => {
          await api("/api/complaints/", { method: "POST", body });
          onSaved();
        }}
      />
    </Card>
  );
}
function Manage({ row, onSaved, staff }) {
  const user = useIdentity();
  return (
    <div className="hs-stack">
      {["DIRECTOR", "WARDEN"].includes(user.role) &&
      row.status !== "Resolved" ? (
        <ResourceForm
          title="Assign maintenance staff"
          fields={[
            {
              name: "assigned_to",
              label: "Maintenance staff",
              options: staff.map((x) => ({ value: x.id, label: x.name })),
            },
          ]}
          onSave={async (body) => {
            await api(`/api/complaints/${row.id}/assign/`, {
              method: "POST",
              body,
            });
            onSaved();
          }}
        />
      ) : null}
      {row.status !== "Resolved" &&
      row.assigned_to &&
      ["DIRECTOR", "MAINTENANCE_STAFF"].includes(user.role) ? (
        <ResourceForm
          title="Update progress"
          fields={[
            {
              name: "status",
              label: "Next status",
              options: [row.status === "Open" ? "In Progress" : "Resolved"],
            },
            {
              name: "remarks",
              label: "Progress remarks",
              type: "textarea",
              maxLength: 2000,
            },
          ]}
          onSave={async (body) => {
            await api(`/api/complaints/${row.id}/progress/`, {
              method: "POST",
              body,
            });
            onSaved();
          }}
        />
      ) : null}
    </div>
  );
}
export default function ComplaintList({ detailId }) {
  const user = useIdentity(),
    student = user.role === "STUDENT";
  const { data, error, refresh } = useResource([
    "/api/complaints/",
    ["DIRECTOR", "WARDEN"].includes(user.role)
      ? "/api/choices/users/?role=MAINTENANCE_STAFF"
      : null,
  ]);
  const [selected, setSelected] = useState(null);
  const [open, setOpen] = useState(false),
    [notice, setNotice] = useState(""),
    [query, setQuery] = useState(""),
    [status, setStatus] = useState("Active");
  let rows = (data?.[0] || [])
    .filter(
      (x) =>
        detailId ||
        ((status === "All" ||
          (status === "Active" && x.status !== "Resolved") ||
          x.status === status) &&
          `${x.student_name} ${x.description} ${x.category}`
            .toLowerCase()
            .includes(query.toLowerCase())),
    )
    .filter((x) => !detailId || String(x.id) === String(detailId));
  return (
    <>
      <PageHeader
        title={student ? "My complaints" : "Complaint management"}
        description="Maintenance requests, assignment and progress history."
      />
      <ErrorMessage error={error} />
      {notice ? (
        <p className="hs-success" role="status">
          {notice}
        </p>
      ) : null}
      {!detailId ? (
        <>
          <div className="hs-toolbar">
            <label>
              Search complaints
              <input
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Student, issue or category"
              />
            </label>
            <label>
              Status
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
              >
                {["Active", "Open", "In Progress", "Resolved", "All"].map(
                  (x) => (
                    <option key={x}>{x}</option>
                  ),
                )}
              </select>
            </label>
            {student ? (
              <Button variant="primary" onClick={() => setOpen(true)}>
                + New complaint
              </Button>
            ) : null}
          </div>
          <Card>
            <DataTable
              headers={[
                "Issue",
                "Student / room",
                "Status",
                "Assigned to",
                "Action",
              ]}
              rows={rows.map((x) => [
                <span key="issue">
                  <strong>
                    #{x.id} · {x.category}
                  </strong>
                  <small className="hs-cell-sub">{x.description}</small>
                </span>,
                `${x.student_name} · ${x.room_snapshot}`,
                <StatusBadge key="status">{x.status}</StatusBadge>,
                x.assigned_name || "Awaiting assignment",
                <Link
                  className="hs-button"
                  key="view"
                  href={`/complaints/${x.id}`}
                >
                  Open complaint
                </Link>,
              ])}
            />
          </Card>
        </>
      ) : null}
      {open ? (
        <Dialog title="Report an issue" onClose={() => setOpen(false)}>
          <ComplaintForm
            onSaved={() => {
              setOpen(false);
              setNotice(
                "Complaint submitted. Your Warden can assign it for repair.",
              );
              refresh();
            }}
          />
        </Dialog>
      ) : null}
      <div className="hs-stack">
        {(detailId ? rows : []).map((x) => (
          <Card key={x.id}>
            <div className="hs-row">
              <h2>
                #{x.id} · {x.category}
              </h2>
              <StatusBadge>{x.status}</StatusBadge>
            </div>
            <p>{x.description}</p>
            <p className="hs-muted">
              Room: {x.room_snapshot} · {dateTime(x.created_at)}
            </p>
            <p className="hs-muted">
              Assigned staff: {x.assigned_name || "Not assigned"}
            </p>
            {!detailId ? (
              <div className="hs-actions">
                <Link className="hs-button" href={`/complaints/${x.id}`}>
                  Open complaint
                </Link>
                <Button
                  onClick={() => setSelected(selected === x.id ? null : x.id)}
                >
                  {selected === x.id ? "Hide history" : "Show history"}
                </Button>
              </div>
            ) : null}
            {detailId || selected === x.id ? (
              <>
                <h3 style={{ marginTop: 20 }}>Activity</h3>
                <HistoryTimeline items={x.transitions} />
              </>
            ) : null}
            {!student ? (
              <Manage row={x} staff={data?.[1] || []} onSaved={refresh} />
            ) : null}
          </Card>
        ))}
      </div>
      {data && !rows.length ? (
        <p className="hs-empty">No complaints found.</p>
      ) : null}
      {!data && !error ? <p role="status">Loading complaints…</p> : null}
    </>
  );
}
