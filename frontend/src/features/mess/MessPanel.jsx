"use client";
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
import DataTable from "@/components/ui/DataTable";
import Dialog from "@/components/ui/Dialog";
import { api } from "@/lib/api";
import { dateTime } from "@/lib/format";
export default function MessPanel() {
  const user = useIdentity(),
    student = user.role === "STUDENT",
    warden = user.role === "WARDEN";
  const { data, error, refresh } = useResource([
    "/api/mess/",
    "/api/mess/coupons/",
    "/api/mess/options/",
    "/api/mess/history/",
    !student ? "/api/choices/users/" : null,
  ]);
  const [failure, setFailure] = useState(null),
    [busy, setBusy] = useState(null),
    [message, setMessage] = useState(""),
    [modal, setModal] = useState(null),
    [editing, setEditing] = useState(null),
    [query, setQuery] = useState("");
  const allocations = data?.[0] || [],
    coupons = data?.[1] || [],
    options = data?.[2] || [],
    history = data?.[3] || [],
    students = (data?.[4] || []).map((x) => ({ value: x.id, label: x.name }));
  const selected = allocations[0];
  async function choose(o) {
    if (
      !window.confirm(
        `Choose ${o.name}? This replaces your current mess selection immediately.`,
      )
    )
      return;
    setBusy(o.id);
    setFailure(null);
    try {
      await api("/api/mess/select/", {
        method: "POST",
        body: { option: o.id },
      });
      setMessage(`You are now enrolled in ${o.name}.`);
      refresh();
    } catch (e) {
      setFailure(e);
    } finally {
      setBusy(null);
    }
  }
  const optionFields = [
    { name: "name", label: "Mess name" },
    { name: "diet", label: "Meal type", options: ["Vegetarian", "Mixed"] },
    {
      name: "description",
      label: "Description",
      type: "textarea",
      optional: true,
    },
    { name: "capacity", label: "Capacity", type: "number", min: 1, step: 1 },
    { name: "breakfast", label: "Breakfast menu", optional: true },
    { name: "lunch", label: "Lunch menu", optional: true },
    { name: "dinner", label: "Dinner menu", optional: true },
    { name: "timings", label: "Meal timings" },
    { name: "active", label: "Accept new selections", type: "checkbox" },
  ];
  return (
    <>
      <PageHeader
        title={student ? "Mess & meals" : "Mess management"}
        description={
          student
            ? "Choose the mess that suits you. Compare meals, timings and available places."
            : "Publish clear meal choices, review enrolments and manage meal coupons."
        }
      >
        <div className="hs-actions">
          {warden ? (
            <Button
              variant="primary"
              onClick={() => {
                setEditing(null);
                setModal("option");
              }}
            >
              + Add mess option
            </Button>
          ) : null}
          {!student ? (
            <>
              <Button onClick={() => setModal("assign")}>
                Select for student
              </Button>
              <Button onClick={() => setModal("coupon")}>+ Issue coupon</Button>
            </>
          ) : null}
        </div>
      </PageHeader>
      <ErrorMessage error={error || failure} />
      {message ? (
        <p role="status" className="hs-success">
          {message}
        </p>
      ) : null}
      {!data && !error ? <p role="status">Loading meal choices…</p> : null}
      {student ? (
        <div className="hs-selected-strip">
          <div>
            <span className="hs-eyebrow">YOUR CURRENT MESS</span>
            <h2>{selected?.mess_name || "No mess selected yet"}</h2>
            <p className="hs-muted">
              {selected
                ? "You can change your choice below when a place is available."
                : "Explore the options below to enrol."}
            </p>
          </div>
          <StatusBadge>{selected ? "Enrolled" : "Choose a mess"}</StatusBadge>
        </div>
      ) : null}
      <section className="hs-section">
        <div className="hs-section-title">
          <h2>{student ? "Explore mess options" : "Mess catalogue"}</h2>
          <span className="hs-muted">Capacity is checked when saving</span>
        </div>
        <div className="hs-mess-grid">
          {options.map((o) => {
            const current = selected?.option === o.id && student;
            return (
              <Card key={o.id}>
                <div className="hs-row">
                  <span className="hs-diet-label">{o.diet}</span>
                  <StatusBadge>
                    {!o.active
                      ? "Inactive"
                      : current
                        ? "Your selection"
                        : o.available === 0
                          ? "Full"
                          : `${o.available} ${o.available === 1 ? "place" : "places"} left`}
                  </StatusBadge>
                </div>
                <h2 className="hs-mess-name">{o.name}</h2>
                <p className="hs-muted">
                  {o.description || "Ask the mess desk about today’s meals."}
                </p>
                <dl className="hs-menu-list">
                  {[
                    ["Breakfast", o.breakfast],
                    ["Lunch", o.lunch],
                    ["Dinner", o.dinner],
                  ].map(([label, value]) => (
                    <div key={label}>
                      <dt>{label}</dt>
                      <dd>{value || "Menu not published"}</dd>
                    </div>
                  ))}
                </dl>
                <p className="hs-meal-times">{o.timings}</p>
                {student ? (
                  <Button
                    variant={current ? "default" : "primary"}
                    disabled={
                      busy !== null || current || o.available === 0 || !o.active
                    }
                    onClick={() => choose(o)}
                  >
                    {busy === o.id
                      ? "Selecting…"
                      : current
                        ? "Currently selected"
                        : o.available === 0
                          ? "No places available"
                          : "Choose this mess"}
                  </Button>
                ) : (
                  <div className="hs-row">
                    <span className="hs-muted">
                      {o.enrolled || 0} / {o.capacity} enrolled
                    </span>
                    {warden ? (
                      <Button
                        onClick={() => {
                          setEditing(o);
                          setModal("option");
                        }}
                      >
                        Edit menu & capacity
                      </Button>
                    ) : null}
                  </div>
                )}
              </Card>
            );
          })}
        </div>
        {data && !options.length ? (
          <p className="hs-empty">
            No mess options have been published. Contact your Warden.
          </p>
        ) : null}
      </section>
      {!student ? (
        <section className="hs-section">
          <div className="hs-section-title">
            <h2>Student enrolments</h2>
            <label className="hs-inline-search">
              Search enrolments
              <input
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Student or mess"
              />
            </label>
          </div>
          <Card>
            <DataTable
              headers={["Student", "Selected mess", "Last updated"]}
              rows={allocations
                .filter((x) =>
                  `${x.student_name} ${x.mess_name}`
                    .toLowerCase()
                    .includes(query.toLowerCase()),
                )
                .map((x) => [
                  x.student_name,
                  x.mess_name,
                  dateTime(x.updated_at),
                ])}
            />
            {data && !allocations.length ? (
              <p className="hs-empty">No enrolments yet.</p>
            ) : null}
          </Card>
        </section>
      ) : null}
      <div className="hs-grid hs-section">
        <Card>
          <h2>{student ? "Your meal coupons" : "Meal coupons"}</h2>
          {coupons.map((c) => (
            <div className="hs-list-item" key={c.id}>
              <div className="hs-row">
                <span>
                  <strong>{c.code}</strong>
                  {!student ? (
                    <small className="hs-cell-sub">{c.student_name}</small>
                  ) : null}
                </span>
                <StatusBadge>{c.active ? "Active" : "Inactive"}</StatusBadge>
              </div>
              <p className="hs-muted">
                {c.valid_from} to {c.valid_to}
              </p>
              {!student ? (
                <Button
                  onClick={async () => {
                    try {
                      await api(`/api/mess/coupons/${c.id}/`, {
                        method: "PATCH",
                        body: { active: !c.active },
                      });
                      refresh();
                    } catch (e) {
                      setFailure(e);
                    }
                  }}
                >
                  {c.active ? "Deactivate" : "Activate"}
                </Button>
              ) : null}
            </div>
          ))}
          {data && !coupons.length ? (
            <p className="hs-muted">No current meal coupons.</p>
          ) : null}
        </Card>
        <Card>
          <h2>Selection history</h2>
          {history.slice(0, 8).map((h) => (
            <div className="hs-list-item" key={h.id}>
              <strong>{h.new_mess}</strong>
              {!student ? (
                <small className="hs-cell-sub">{h.student_name}</small>
              ) : null}
              <p className="hs-muted">
                {h.old_mess ? `Changed from ${h.old_mess}` : "First selection"}{" "}
                · {dateTime(h.occurred_at)}
              </p>
            </div>
          ))}
          {data && !history.length ? (
            <p className="hs-muted">Mess changes will appear here.</p>
          ) : null}
        </Card>
      </div>
      {modal ? (
        <Dialog
          title={
            modal === "option"
              ? editing
                ? "Edit mess option"
                : "New mess option"
              : modal === "assign"
                ? "Select a mess for a student"
                : "Issue meal coupon"
          }
          onClose={() => setModal(null)}
        >
          <ResourceForm
            title="Details"
            key={editing?.id || modal}
            fields={
              modal === "option"
                ? optionFields
                : modal === "assign"
                  ? [
                      { name: "student", label: "Student", options: students },
                      {
                        name: "option",
                        label: "Mess option",
                        options: options
                          .filter((o) => o.active)
                          .map((o) => ({
                            value: o.id,
                            label: `${o.name} · ${o.available} available`,
                          })),
                      },
                    ]
                  : [
                      { name: "student", label: "Student", options: students },
                      { name: "code", label: "Coupon code", maxLength: 80 },
                      { name: "valid_from", label: "Valid from", type: "date" },
                      { name: "valid_to", label: "Valid until", type: "date" },
                      { name: "active", label: "Active", type: "checkbox" },
                    ]
            }
            initial={
              modal === "option"
                ? editing || {
                    active: true,
                    capacity: 100,
                    timings: "Breakfast 7–9 AM · Lunch 12–2 PM · Dinner 7–9 PM",
                  }
                : { active: true }
            }
            button="Save changes"
            onSave={async (body) => {
              await api(
                modal === "option"
                  ? `/api/mess/options/${editing ? editing.id + "/" : ""}`
                  : modal === "assign"
                    ? "/api/mess/select/"
                    : "/api/mess/coupons/",
                {
                  method: modal === "option" && editing ? "PATCH" : "POST",
                  body,
                },
              );
              setModal(null);
              setEditing(null);
              setMessage("Mess details updated.");
              refresh();
            }}
          />
        </Dialog>
      ) : null}
    </>
  );
}
