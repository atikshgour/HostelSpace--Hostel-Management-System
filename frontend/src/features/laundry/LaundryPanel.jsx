"use client";
import { useState } from "react";
import { usePathname } from "next/navigation";
import {
  useResource,
  useIdentity,
  ErrorMessage,
  ResourceForm,
} from "@/components/ui/AppShell";
import Card from "@/components/ui/Card";
import PageHeader from "@/components/ui/PageHeader";
import Button from "@/components/ui/Button";
import DataTable from "@/components/ui/DataTable";
import StatusBadge from "@/components/ui/StatusBadge";
import Dialog from "@/components/ui/Dialog";
import { api } from "@/lib/api";
import { dateTime } from "@/lib/format";
export default function LaundryPanel() {
  const user = useIdentity(),
    staff = user.role === "LAUNDRY_STAFF",
    student = user.role === "STUDENT",
    path = usePathname(),
    scheduleView = (path || "").endsWith("/manage");
  const { data, error, refresh } = useResource([
    "/api/laundry/allocations/",
    "/api/laundry/records/",
    staff ? "/api/choices/users/" : null,
    "/api/laundry/policy/",
  ]);
  const [failure, setFailure] = useState(null),
    [busy, setBusy] = useState(null),
    [open, setOpen] = useState(false),
    [policyOpen, setPolicyOpen] = useState(false),
    [query, setQuery] = useState(""),
    [filter, setFilter] = useState("Active"),
    [notice, setNotice] = useState("");
  const plans = data?.[0] || [],
    records = data?.[1] || [],
    plan = plans[0];
  const options = (data?.[2] || []).map((x) => ({
    value: x.id,
    label: `${x.name} · ${plans.find((p) => p.student === x.id)?.srn || x.id}`,
  }));
  async function transition(row, action) {
    if (
      action === "collect" &&
      !window.confirm(
        `Confirm ${row.student_name} has collected batch #${row.id}?`,
      )
    )
      return;
    setBusy(row.id);
    setFailure(null);
    try {
      await api(`/api/laundry/records/${row.id}/${action}/`, {
        method: "POST",
        body: {},
      });
      setNotice(
        action === "ready"
          ? "Batch is ready. The student can see the update."
          : "Collection confirmed. The receipt remains in history.",
      );
      refresh();
    } catch (e) {
      setFailure(e);
    } finally {
      setBusy(null);
    }
  }
  const visible = records.filter(
    (x) =>
      (filter === "All" ||
        (filter === "Active" && x.status !== "Collected") ||
        x.status === filter) &&
      `${x.student_name} ${x.item_details} ${x.id}`
        .toLowerCase()
        .includes(query.toLowerCase()),
  );
  return (
    <>
      <PageHeader
        title={
          student
            ? "My laundry"
            : scheduleView
              ? "Laundry group schedule"
              : "Laundry desk"
        }
        description="Automatic weekly groups with return dates set by your laundry team."
      >
        {staff && !scheduleView ? (
          <Button variant="primary" onClick={() => setOpen(true)}>
            + Receive clothes
          </Button>
        ) : null}
      </PageHeader>
      <ErrorMessage error={error || failure} />
      {staff ? (
        <div className="hs-policy-line">
          <span>
            Default return time:{" "}
            <strong>{data?.[3]?.turnaround_days || 3} days</strong>
          </span>
          <Button onClick={() => setPolicyOpen(true)}>
            Change return time
          </Button>
        </div>
      ) : null}
      {notice ? (
        <p role="status" className="hs-success">
          {notice}
        </p>
      ) : null}
      {!data && !error ? <p role="status">Loading laundry…</p> : null}
      {student ? (
        <div className="hs-stats hs-three">
          <Card>
            <span className="hs-eyebrow">YOUR GROUP</span>
            <p className="hs-stat">Group {plan?.group_number || "—"}</p>
            <p>{plan?.weekday || "Loading…"} drop-off</p>
          </Card>
          <Card>
            <span className="hs-eyebrow">NEXT DROP-OFF</span>
            <p className="hs-stat hs-date-stat">
              {plan?.next_dropoff_date || "—"}
            </p>
            <p className="hs-muted">
              Bring your clothes to the laundry counter.
            </p>
          </Card>
          <Card>
            <span className="hs-eyebrow">SCHEDULED RETURN</span>
            <p className="hs-stat hs-date-stat">
              {plan?.next_return_date || "—"}
            </p>
            <p className="hs-muted">
              Actual ready status is confirmed by staff.
            </p>
          </Card>
        </div>
      ) : (
        <div className="hs-notice">
          Groups are calculated from the numeric part of the student number:
          (number − 1) modulo 7. Group 1 = Monday, through Group 7 = Sunday.
          Staff may receive an off-day handover; its return date is always
          receipt date + the return time selected by staff. Existing batches
          keep their original expected return dates.
        </div>
      )}
      {scheduleView && !student ? (
        <section className="hs-section">
          <Card>
            <h2>Student timetable</h2>
            <label className="hs-search-label">
              Search schedule
              <input
                type="search"
                value={query}
                placeholder="Student name or number"
                onChange={(e) => setQuery(e.target.value)}
              />
            </label>
            <DataTable
              headers={[
                "Student",
                "Group",
                "Drop-off day",
                "Next drop-off",
                "Expected return",
              ]}
              rows={plans
                .filter((x) =>
                  `${x.student_name} ${x.srn}`
                    .toLowerCase()
                    .includes(query.toLowerCase()),
                )
                .map((x) => [
                  <span key="student">
                    <strong>{x.student_name}</strong>
                    <small className="hs-cell-sub">
                      {x.srn} · Room {x.room}
                    </small>
                  </span>,
                  `Group ${x.group_number}`,
                  x.weekday,
                  x.next_dropoff_date,
                  x.next_return_date,
                ])}
            />
          </Card>
        </section>
      ) : (
        <section className="hs-section">
          <div className="hs-toolbar">
            <label>
              Search batches
              <input
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Student, items or batch number"
              />
            </label>
            <label>
              Batch status
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              >
                {["Active", "Received", "Ready", "Collected", "All"].map(
                  (x) => (
                    <option key={x}>{x}</option>
                  ),
                )}
              </select>
            </label>
          </div>
          <Card>
            <h2>{student ? "Your batches" : "Work queue"}</h2>
            <DataTable
              headers={[
                "Batch / student",
                "Items",
                "Expected return",
                "Status",
                "Next step",
              ]}
              rows={visible.map((x) => [
                <span key="name">
                  <strong>
                    #{x.id} · {x.student_name}
                  </strong>
                  <small className="hs-cell-sub">
                    Received {dateTime(x.received_at)} · Group{" "}
                    {x.group_number || "—"}
                  </small>
                </span>,
                `${x.item_count} items · ${x.item_details}`,
                x.expected_return_date || "Not recorded",
                <StatusBadge key="status">{x.status}</StatusBadge>,
                x.status === "Collected" ? (
                  <span key="done">
                    Collected
                    <small className="hs-cell-sub">
                      {dateTime(x.collected_at)}
                    </small>
                  </span>
                ) : staff ? (
                  <Button
                    key="action"
                    variant={x.status === "Ready" ? "primary" : "default"}
                    disabled={busy === x.id}
                    onClick={() =>
                      transition(
                        x,
                        x.status === "Received" ? "ready" : "collect",
                      )
                    }
                  >
                    {busy === x.id
                      ? "Saving…"
                      : x.status === "Received"
                        ? "Mark ready"
                        : "Confirm collection"}
                  </Button>
                ) : x.status === "Ready" ? (
                  "Ready at the laundry counter"
                ) : (
                  "Washing in progress"
                ),
              ])}
            />
            {data && !visible.length ? (
              <p className="hs-empty">No batches match this view.</p>
            ) : null}
          </Card>
        </section>
      )}
      {policyOpen ? (
        <Dialog
          title="Default laundry return time"
          onClose={() => setPolicyOpen(false)}
        >
          <p className="hs-muted">
            Applies to future schedules and handovers only. Existing batch dates
            do not change.
          </p>
          <ResourceForm
            title="Turnaround"
            fields={[
              {
                name: "turnaround_days",
                label: "Return after (days)",
                type: "number",
                min: 1,
                max: 14,
                step: 1,
              },
            ]}
            initial={{ turnaround_days: data?.[3]?.turnaround_days || 3 }}
            onSave={async (body) => {
              await api("/api/laundry/policy/", { method: "PUT", body });
              setPolicyOpen(false);
              setNotice("Default return time updated for future batches.");
              refresh();
            }}
          />
        </Dialog>
      ) : null}
      {open ? (
        <Dialog title="Receive clothes" onClose={() => setOpen(false)}>
          <p className="hs-muted">
            Choose the return time for this batch. The group and expected return
            date are calculated automatically.
          </p>
          <ResourceForm
            title="Handover details"
            initial={{ turnaround_days: data?.[3]?.turnaround_days || 3 }}
            fields={[
              { name: "student", label: "Student", options },
              {
                name: "item_details",
                label: "Item details",
                type: "textarea",
                maxLength: 1000,
              },
              {
                name: "item_count",
                label: "Number of items",
                type: "number",
                min: 1,
                step: 1,
              },
              {
                name: "turnaround_days",
                label: "Return after (days)",
                type: "number",
                min: 1,
                max: 14,
                step: 1,
              },
            ]}
            button="Record handover"
            onSave={async (body) => {
              await api("/api/laundry/records/", { method: "POST", body });
              setOpen(false);
              setNotice(
                "Handover recorded with the selected return time. Check the expected return date in the work queue.",
              );
              refresh();
            }}
          />
        </Dialog>
      ) : null}
    </>
  );
}
