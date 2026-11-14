"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ResourceForm, ErrorMessage } from "@/components/ui/AppShell";
import Card from "@/components/ui/Card";
import PageHeader from "@/components/ui/PageHeader";
export default function StudyRoomEditor() {
  const [data, setData] = useState(null),
    [error, setError] = useState(null);
  useEffect(() => {
    api("/api/study-room/").then(setData).catch(setError);
  }, []);
  return (
    <>
      <PageHeader
        title="Manage study room"
        description="Publish Open or Closed status. This is not a booking system."
      />
      <ErrorMessage error={error} />
      {data ? (
        <Card>
          <ResourceForm
            title="Room status"
            initial={data}
            fields={[
              { name: "status", label: "Status", options: ["Open", "Closed"] },
              { name: "timings", label: "Opening hours", optional: true },
              {
                name: "message",
                label: "Message",
                type: "textarea",
                optional: true,
                maxLength: 500,
              },
            ]}
            onSave={(body) => api("/api/study-room/", { method: "PUT", body })}
          />
        </Card>
      ) : null}
    </>
  );
}
