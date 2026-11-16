"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ErrorMessage } from "@/components/ui/AppShell";
import Card from "@/components/ui/Card";
import StatusBadge from "@/components/ui/StatusBadge";
import PageHeader from "@/components/ui/PageHeader";
import { dateTime } from "@/lib/format";
export default function StudyRoomCard() {
  const [data, setData] = useState(null),
    [error, setError] = useState(null);
  useEffect(() => {
    api("/api/study-room/").then(setData).catch(setError);
  }, []);
  return (
    <>
      <PageHeader
        title="Study room"
        description="Check the latest room status before you head over."
      />
      <ErrorMessage error={error} />
      {data ? (
        <Card>
          <div className="hs-row">
            <h2>Hostel study room</h2>
            <StatusBadge>{data.status}</StatusBadge>
          </div>
          <p>{data.timings || "No timings published"}</p>
          <p className="hs-notice">
            {data.message || "No additional message."}
          </p>
          <small className="hs-muted">
            Last updated: {dateTime(data.updated_at)}
          </small>
        </Card>
      ) : (
        <p role="status">Loading study room…</p>
      )}
    </>
  );
}
