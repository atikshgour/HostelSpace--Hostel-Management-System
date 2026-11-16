"use client";
import Link from "next/link";
import {
  useIdentity,
  useResource,
  ErrorMessage,
} from "@/components/ui/AppShell";
import Card from "@/components/ui/Card";
import PageHeader from "@/components/ui/PageHeader";
import { roleLabel } from "@/lib/roles";
const destinations = {
  STUDENT: [
    ["Request leave", "/leave", "Submit dates and follow your approval."],
    ["Report an issue", "/complaints", "Tell us what needs fixing."],
    ["View your mess", "/mess", "View your assigned mess and valid coupons."],
  ],
  WARDEN: [
    ['Review leave','/leave/review','Review your assigned students.'],
    ['Attendance sessions','/attendance/manage','Configure and review attendance.'],
    ['Deviation records','/deviations/manage','Record authorized rule deviations.'],
  ],
  LAUNDRY_STAFF: [
    [
      "Receive clothes",
      "/laundry/handover",
      "Record items. Return dates are automatic.",
    ],
    [
      "View group schedule",
      "/laundry/manage",
      "See drop-off days for each student.",
    ],
  ],
  MESS_STAFF: [
    ["Mess desk", "/mess/manage", "View enrolments and issue meal coupons."],
  ],
  MAINTENANCE_STAFF: [
    [
      "My work queue",
      "/complaints/manage",
      "Update assigned repairs and close completed work.",
    ],
  ],
  DIRECTOR: [
    ["Hostel reports", "/director", "Review live operational summaries."],
    [
      "Account oversight",
      "/director/users",
      "Review existing accounts and assignments.",
    ],
  ],
  CONTENT_STAFF: [
    [
      "Publish an update",
      "/information/manage",
      "Maintain notices, contacts and rules.",
    ],
  ],
  CHIEF_WARDEN: [
    ["Escalated leave", "/leave/review", "Review requests sent by Wardens."],
  ],
};
export default function Dashboard() {
  const user = useIdentity(),
    { data, error } = useResource(["/api/overview/"]);
  const d = data?.[0] || {};
  const student = user.role === "STUDENT";
  const stats = student
    ? [
        ["Pending leave", d.pending_leave, "/leave"],
        ["Open complaints", d.open_complaints, "/complaints"],
        ["Unpaid dues", d.unpaid_fees, "/fees"],
        ["Laundry ready", d.laundry_ready, "/laundry"],
      ]
    : user.role === "LAUNDRY_STAFF"
      ? [
          ["In washing", d.laundry_received, "/laundry/handover"],
          ["Ready to collect", d.laundry_ready, "/laundry/handover"],
          ["Students scheduled", d.active_students, "/laundry/manage"],
        ]
      : user.role === "MAINTENANCE_STAFF"
        ? [["Open assigned jobs", d.open_complaints, "/complaints/manage"]]
        : [
            ["Active students", d.active_students, "/director/users"],
            ["Pending leave", d.pending_leave, "/leave/review"],
            ["Open complaints", d.open_complaints, "/complaints/manage"],
          ];
  const visibleStats = stats.filter((x) => user.role !== "WARDEN" || ["Pending leave"].includes(x[0]));
  return (
    <>
      <PageHeader
        title={`Welcome back, ${user.name.split(" ")[0]}`}
        description={
          student
            ? "Your day at a glance. Everything you need, without the clutter."
            : `${roleLabel(user.role)} workspace · Focus on what needs attention.`
        }
      />
      <ErrorMessage error={error} />
      {!data && !error ? <p role="status">Loading your workspace…</p> : null}
      <div className="hs-stats">
        {visibleStats
          .filter(
            (x) =>
              user.role === "STUDENT" ||
              [
                "WARDEN",
                "DIRECTOR",
                "LAUNDRY_STAFF",
                "MAINTENANCE_STAFF",
              ].includes(user.role),
          )
          .map(([label, value, url]) => (
            <Link
              href={
                user.role === "DIRECTOR" && url === "/leave/review"
                  ? "/director"
                  : url
              }
              className="hs-card hs-stat-card"
              key={label}
            >
              <span>{label}</span>
              <strong>{value ?? "—"}</strong>
              <span className="hs-stat-caption">View details ↗</span>
            </Link>
          ))}
      </div>
      <div className="hs-dashboard-grid">
        <section>
          <div className="hs-section-title">
            <h2>Get things done</h2>
            <span className="hs-muted">Quick actions</span>
          </div>
          <Card>
            {(destinations[user.role] || []).map(([name, url, desc]) => (
              <Link className="hs-action-row" href={url} key={url}>
                <span>
                  <strong>{name}</strong>
                  <small>{desc}</small>
                </span>
                <span aria-hidden="true">→</span>
              </Link>
            ))}
          </Card>
        </section>
        <section>
          <div className="hs-section-title">
            <h2>{student ? "Your next essentials" : "Hostel updates"}</h2>
          </div>
          <Card>
            {student ? (
              <>
                <div className="hs-list-item">
                  <span className="hs-eyebrow">
                    LAUNDRY · GROUP {d.laundry?.group_number || "—"}
                  </span>
                  <h3>{d.laundry?.weekday || "Loading…"} drop-off</h3>
                  <p className="hs-muted">
                    Next: {d.laundry?.next_dropoff_date || "—"} · Expected
                    return: {d.laundry?.next_return_date || "—"}
                  </p>
                  <Link href="/laundry">View laundry →</Link>
                </div>
                <div className="hs-list-item">
                  <span className="hs-eyebrow">YOUR MESS</span>
                  <h3>{d.mess || "View your mess"}</h3>
                  <Link href="/mess">Explore meals & choices →</Link>
                </div>
              </>
            ) : null}
            <div className="hs-list-item">
              <span className="hs-eyebrow">STUDY ROOM</span>
              <h3>{d.study_room || "—"}</h3>
              <p className="hs-muted">
                Check current hours before heading over.
              </p>
            </div>
          </Card>
        </section>
      </div>
      <section className="hs-section">
        <div className="hs-section-title">
          <h2>Latest announcements</h2>
          <Link href="/information">View information →</Link>
        </div>
        <div className="hs-notice-grid">
          {(d.notices || []).map((n) => (
            <Card key={n.id}>
              <span className="hs-eyebrow">ANNOUNCEMENT</span>
              <h3>{n.title}</h3>
              <p className="hs-muted">{n.body}</p>
            </Card>
          ))}
        </div>
        {data && !d.notices?.length ? (
          <p className="hs-empty">No announcements right now.</p>
        ) : null}
      </section>
    </>
  );
}
