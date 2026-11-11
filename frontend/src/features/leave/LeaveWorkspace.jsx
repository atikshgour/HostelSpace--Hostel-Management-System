"use client";
/* Arin Singh | US-05/06 | Sprint 3. */
import { useState, useEffect } from "react";
import { request } from "../arin/api";
import {
  useIdentity,
  useRows,
  Frame,
  Field,
  ErrorBox,
  Pager,
  Timeline,
  styles,
} from "../arin/common";
function LeaveForm({ refresh }) {
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(null),
    [message, setMessage] = useState("");
  async function submit(e) {
    e.preventDefault();
    const form = e.currentTarget;
    const v = Object.fromEntries(new FormData(form));
    setError(null);
    setMessage("");
    if (v.end_date < v.start_date) {
      setError(new Error("End date must be on or after start date."));
      return;
    }
    setBusy(true);
    try {
      await request("/api/leaves/", { method: "POST", body: v });
      form.reset();
      setMessage("Leave submitted with Pending status.");
      refresh();
    } catch (x) {
      setError(x);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className={styles.card}>
      <h2>Apply for leave</h2>
      <form onSubmit={submit}>
        <div className={styles.grid}>
          <Field label="Start date" name="start_date" type="date" required />
          <Field label="End date" name="end_date" type="date" required />
        </div>
        <Field label="Reason">
          <textarea name="reason" required maxLength={2000} />
        </Field>
        <button disabled={busy}>{busy ? "Submitting…" : "Submit leave"}</button>
        <ErrorBox error={error} />
        <p role="status">{message}</p>
      </form>
    </section>
  );
}
function Decision({ row, role, refresh }) {
  const [decision, setDecision] = useState("Approved"),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(null);
  const allowed =
    (row.status === "Pending" && role === "WARDEN") ||
    (row.status === "Escalated" && role === "CHIEF_WARDEN");
  if (!allowed) return null;
  async function submit(e) {
    e.preventDefault();
    const v = new FormData(e.currentTarget);
    setBusy(true);
    setError(null);
    try {
      await request(`/api/leaves/${row.id}/decision/`, {
        method: "POST",
        body: { decision, remarks: v.get("remarks") },
      });
      refresh();
    } catch (x) {
      setError(x);
    } finally {
      setBusy(false);
    }
  }
  return (
    <form onSubmit={submit}>
      <Field label="Decision">
        <select value={decision} onChange={(e) => setDecision(e.target.value)}>
          <option>Approved</option>
          <option>Rejected</option>
          {role === "WARDEN" ? <option>Escalated</option> : null}
        </select>
      </Field>
      <Field label="Decision remarks">
        <textarea required name="remarks" maxLength={2000} />
      </Field>
      <button disabled={busy}>{busy ? "Saving…" : "Save decision"}</button>
      <ErrorBox error={error} />
    </form>
  );
}
function LeaveRecords({ role, revision, refresh, detailId }) {
  const data = useRows("/api/leaves/", revision);
  const [detail, setDetail] = useState(null),
    [err, setErr] = useState(null);
  useEffect(() => {
    let live = true;
    if (detailId) {
      request(`/api/leaves/${detailId}/`)
        .then((x) => live && setDetail(x))
        .catch((e) => live && setErr(e));
    }
    return () => {
      live = false;
    };
  }, [detailId, revision]);
  // Detail route never assumes a row from a different student's list is accessible.
  const rows = detailId ? (detail ? [detail] : []) : data.rows;
  async function loadDetail() {
    setErr(null);
    try {
      setDetail(await request(`/api/leaves/${detailId}/`));
    } catch (e) {
      setErr(e);
    }
  }
  return (
    <section>
      <h2>
        {role === "STUDENT" ? "My leave history" : "Assigned leave queue"}
      </h2>
      {detailId ? (
        <button onClick={loadDetail}>Load / refresh request</button>
      ) : null}
      <ErrorBox error={err || data.error} />
      {data.loading ? <p role="status">Loading requests…</p> : null}
      {!data.loading && !rows.length ? <p>No records</p> : null}
      {rows.map((row) => (
        <article className={styles.card} key={row.id}>
          <h3>
            {row.start_date} to {row.end_date} · {row.status}
          </h3>
          <p>{row.reason}</p>
          <p className={styles.muted}>
            Request {row.id} · Student {row.student}
          </p>
          <Timeline items={row.transitions} />
          <Decision
            row={row}
            role={role}
            refresh={() => {
              refresh();
              if (detailId) loadDetail();
            }}
          />
          {!detailId ? <a href={"/leave/" + row.id}>Open request</a> : null}
        </article>
      ))}
      {!detailId ? <Pager data={data} /> : null}
    </section>
  );
}
export default function LeaveWorkspace({ detailId }) {
  const identity = useIdentity(),
    [revision, setRevision] = useState(0);
  const role = identity.user?.role;
  const refresh = () => setRevision((x) => x + 1);
  return (
    <Frame title="Leave requests" identity={identity}>
      {!["STUDENT", "WARDEN", "CHIEF_WARDEN"].includes(role) ? (
        <p>This role has no leave workflow access.</p>
      ) : (
        <>
          {role === "STUDENT" && !detailId ? (
            <LeaveForm refresh={refresh} />
          ) : null}
          <LeaveRecords
            role={role}
            revision={revision}
            refresh={refresh}
            detailId={detailId}
          />
        </>
      )}
    </Frame>
  );
}

export { LeaveForm, LeaveRecords, Decision };
