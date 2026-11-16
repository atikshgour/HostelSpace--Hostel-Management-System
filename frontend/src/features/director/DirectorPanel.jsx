"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ErrorMessage } from "@/components/ui/AppShell";
import Card from "@/components/ui/Card";
import PageHeader from "@/components/ui/PageHeader";
import DataTable from "@/components/ui/DataTable";
import { dateTime } from "@/lib/format";
export default function DirectorPanel() {
  const [data, setData] = useState(null),
    [error, setError] = useState(null);
  useEffect(() => {
    api("/api/director/summary/").then(setData).catch(setError);
  }, []);
  return (
    <>
      <PageHeader
        title="Director overview"
        description="Read-only summaries from the live owning-module records."
      />
      <ErrorMessage error={error} />
      {data ? (
        <>
          <div className="hs-grid">
            {[
              ["Pending leave", data.pending_leave],
              ["Escalated leave", data.escalated_leave],
              ["Open complaints", data.open_complaints],
              ["Unpaid fees", data.unpaid_fees],
              ["Active students", data.active_students],
            ].map(([k, v]) => (
              <Card key={k}>
                <p className="hs-muted">{k}</p>
                <p className="hs-stat">{v}</p>
              </Card>
            ))}
          </div>
          <Card style={{ marginTop: 24 }}>
            <h2>Attendance by session</h2>
            <DataTable
              headers={["Session", "Opens", "Accepted records"]}
              rows={data.attendance_by_session.map((x) => [
                x.title,
                dateTime(x.opens_at),
                x.accepted,
              ])}
            />
            {!data.attendance_by_session.length ? (
              <p className="hs-empty">No attendance sessions.</p>
            ) : null}
          </Card>
        </>
      ) : !error ? (
        <p role="status">Loading summaries…</p>
      ) : null}
    </>
  );
}
