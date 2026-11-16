"use client";
/* Existing leave API and transaction rules retained; task-focused presentation. */
import Link from "next/link";
import { useEffect, useState } from "react";
import {
  decideLeave,
  getIdentity,
  getLeave,
  listLeaves,
  submitLeave,
} from "./api";
import { ErrorMessage as SharedError } from "@/components/ui/AppShell";
import Card from "@/components/ui/Card";
import PageHeader from "@/components/ui/PageHeader";
import Button from "@/components/ui/Button";
import StatusBadge from "@/components/ui/StatusBadge";
import DataTable from "@/components/ui/DataTable";
import Dialog from "@/components/ui/Dialog";
export const ErrorMessage = SharedError;
export function LeaveForm({ onSaved }) {
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(null);
  async function submit(e) {
    e.preventDefault();
    const body = Object.fromEntries(new FormData(e.currentTarget));
    setError(null);
    if (body.end_date < body.start_date) {
      setError(new Error("End date must be on or after start date."));
      return;
    }
    setBusy(true);
    try {
      await submitLeave(body);
      onSaved();
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  return (
    <form method="post" onSubmit={submit}>
      <h2>Apply for leave</h2>
      <p className="hs-muted">
        Your request goes to your assigned Warden. Wait for approval before
        leaving.
      </p>
      <div className="hs-grid">
        <label className="hs-field">
          Start date
          <input name="start_date" type="date" required />
        </label>
        <label className="hs-field">
          End date
          <input name="end_date" type="date" required />
        </label>
      </div>
      <label className="hs-field">
        Reason
        <textarea name="reason" maxLength={2000} required />
      </label>
      <ErrorMessage error={error} />
      <Button variant="primary" disabled={busy}>
        {busy ? "Submitting…" : "Submit leave"}
      </Button>
    </form>
  );
}
export function LeaveHistory({ transitions = [] }) {
  return (
    <ol className="hs-timeline">
      {transitions.map((t) => (
        <li key={t.id}>
          <strong>
            {t.from_status || "New"} → {t.to_status}
          </strong>
          <p>{t.remarks}</p>
          <small className="hs-muted">
            {t.actor_name || "Authorized staff"} ·{" "}
            {new Date(t.occurred_at).toLocaleString()}
          </small>
        </li>
      ))}
    </ol>
  );
}
export function LeaveReviewPanel({ row, role, onSaved }) {
  const [decision, setDecision] = useState("Approved"),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(null);
  if (
    !(
      (row.status === "Pending" && role === "WARDEN") ||
      (row.status === "Escalated" && role === "CHIEF_WARDEN")
    )
  )
    return null;
  async function save(e) {
    e.preventDefault();
    if (
      !window.confirm(
        `Confirm decision: ${decision}? Final approvals and rejections cannot be changed.`,
      )
    )
      return;
    setBusy(true);
    setError(null);
    try {
      await decideLeave(row.id, {
        decision,
        remarks: new FormData(e.currentTarget).get("remarks"),
      });
      onSaved();
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  return (
    <form method="post" onSubmit={save} className="hs-section">
      <h2>Review request</h2>
      <label className="hs-field">
        Decision
        <select value={decision} onChange={(e) => setDecision(e.target.value)}>
          <option>Approved</option>
          <option>Rejected</option>
          {role === "WARDEN" ? <option>Escalated</option> : null}
        </select>
      </label>
      <label className="hs-field">
        Decision remarks
        <textarea name="remarks" maxLength={2000} required />
      </label>
      <ErrorMessage error={error} />
      <Button variant="primary" disabled={busy}>
        {busy ? "Saving…" : "Save decision"}
      </Button>
    </form>
  );
}
export default function LeaveWorkspace({ detailId = null }) {
  const [identity, setIdentity] = useState(null),
    [rows, setRows] = useState(null),
    [error, setError] = useState(null),
    [revision, setRevision] = useState(0),
    [open, setOpen] = useState(false),
    [query, setQuery] = useState(""),
    [filter, setFilter] = useState("All"),
    [page, setPage] = useState(1),
    [notice, setNotice] = useState("");
  useEffect(() => {
    let live = true;
    getIdentity()
      .then((u) => {
        if (live) {
          setIdentity(u);
          setFilter(
            u.role === "STUDENT"
              ? "All"
              : u.role === "WARDEN"
                ? "Pending"
                : "Escalated",
          );
        }
      })
      .catch((e) => live && setError(e));
    return () => {
      live = false;
    };
  }, []);
  useEffect(() => {
    let live = true;
    setError(null);
    async function load() {
      if (detailId) return [await getLeave(detailId)];
      let items = [],
        p = 1,
        data;
      do {
        data = await listLeaves(p++);
        items.push(...data.results);
      } while (data.next);
      return items;
    }
    load()
      .then((x) => live && setRows(x))
      .catch((e) => live && setError(e));
    return () => {
      live = false;
    };
  }, [detailId, revision]);
  const role = identity?.role,
    refresh = () => setRevision((x) => x + 1),
    matching = (rows || []).filter(
      (r) =>
        (filter === "All" || r.status === filter) &&
        `${r.student_name || ""} ${r.reason} ${r.id}`
          .toLowerCase()
          .includes(query.toLowerCase()),
    );
  const current = rows?.[0];
  return (
    <>
      <PageHeader
        title={
          detailId
            ? "Leave request"
            : role === "STUDENT"
              ? "My leave requests"
              : "Leave review"
        }
        description={
          detailId
            ? "Request details, decisions and a complete activity trail."
            : role === "STUDENT"
              ? "Submit a request and follow its progress."
              : "Review requests that need your attention."
        }
      >
        {role === "STUDENT" && !detailId ? (
          <Button variant="primary" onClick={() => setOpen(true)}>
            + Request leave
          </Button>
        ) : null}
      </PageHeader>
      <ErrorMessage error={error} />
      {notice ? (
        <p className="hs-success" role="status">
          {notice}
        </p>
      ) : null}
      {!rows && !error ? <p role="status">Loading requests…</p> : null}
      {!detailId ? (
        <>
          <div className="hs-toolbar">
            <label>
              Search requests
              <input
                type="search"
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value);
                  setPage(1);
                }}
                placeholder="Student, reason or request number"
              />
            </label>
            <label>
              Status
              <select
                value={filter}
                onChange={(e) => {
                  setFilter(e.target.value);
                  setPage(1);
                }}
              >
                {["All", "Pending", "Escalated", "Approved", "Rejected"].map(
                  (x) => (
                    <option key={x}>{x}</option>
                  ),
                )}
              </select>
            </label>
          </div>
          <Card>
            <DataTable
              headers={[
                "Student / request",
                "Leave dates",
                "Reason",
                "Status",
                "Action",
              ]}
              rows={matching.slice((page - 1) * 10, page * 10).map((r) => [
                <span key="name">
                  <strong>{r.student_name || "Your request"}</strong>
                  <small className="hs-cell-sub">#{r.id.slice(0, 8)}</small>
                </span>,
                `${r.start_date} → ${r.end_date}`,
                r.reason,
                <StatusBadge key="status">{r.status}</StatusBadge>,
                <Link key="view" className="hs-button" href={`/leave/${r.id}`}>
                  Open request
                </Link>,
              ])}
            />
            {rows && !matching.length ? (
              <p className="hs-empty">No requests match this view.</p>
            ) : null}
          </Card>
          <nav className="hs-pagination" aria-label="Leave pages">
            <Button disabled={page === 1} onClick={() => setPage((x) => x - 1)}>
              Previous
            </Button>
            <span>
              Page {page} · {matching.length} requests
            </span>
            <Button
              disabled={page * 10 >= matching.length}
              onClick={() => setPage((x) => x + 1)}
            >
              Next
            </Button>
          </nav>
        </>
      ) : current ? (
        <>
          <Link href={role === "STUDENT" ? "/leave" : "/leave/review"}>
            ← Back to requests
          </Link>
          <div className="hs-grid hs-section">
            <Card>
              <div className="hs-row">
                <h2>{current.student_name || "Student request"}</h2>
                <StatusBadge>{current.status}</StatusBadge>
              </div>
              <dl className="hs-detail">
                <div>
                  <dt>From</dt>
                  <dd>{current.start_date}</dd>
                </div>
                <div>
                  <dt>To</dt>
                  <dd>{current.end_date}</dd>
                </div>
                <div>
                  <dt>Assigned Warden</dt>
                  <dd>{current.warden_name || "Assigned Warden"}</dd>
                </div>
                <div>
                  <dt>Request number</dt>
                  <dd>{current.id.slice(0, 8)}</dd>
                </div>
              </dl>
              <h3 className="hs-section">Reason for leave</h3>
              <p>{current.reason}</p>
              <LeaveReviewPanel
                row={current}
                role={role}
                onSaved={() => {
                  refresh();
                  setNotice("Decision saved. The student can see the update.");
                }}
              />
            </Card>
            <Card>
              <h2>Request activity</h2>
              <LeaveHistory transitions={current.transitions} />
            </Card>
          </div>
        </>
      ) : null}
      {open ? (
        <Dialog title="New leave request" onClose={() => setOpen(false)}>
          <LeaveForm
            onSaved={() => {
              setOpen(false);
              setNotice("Leave request submitted with Pending status.");
              refresh();
            }}
          />
        </Dialog>
      ) : null}
    </>
  );
}
