"use client";
import { useState } from "react";
import { useIdentity, ResourceForm } from "@/components/ui/AppShell";
import Card from "@/components/ui/Card";
import PageHeader from "@/components/ui/PageHeader";
import { api } from "@/lib/api";
export default function ProfilePanel() {
  const identity = useIdentity();
  const [u, setU] = useState(identity);
  if (u.role !== "STUDENT")
    return <p>Student profiles are available to students only.</p>;
  return (
    <>
      <PageHeader
        title="My profile"
        description="Your personal and hostel information."
      />
      <div className="hs-grid">
        <Card>
          <h2>{u.name}</h2>
          <dl className="hs-detail">
            {Object.entries({
              SRN: u.profile?.srn,
              Hostel: u.profile?.hostel,
              Room: u.profile?.room,
              "Assigned warden": u.profile?.warden_name || "Not assigned",
              Username: u.username,
            }).map(([k, v]) => (
              <div key={k}>
                <dt>{k}</dt>
                <dd>{v || "Not assigned"}</dd>
              </div>
            ))}
          </dl>
          <p className="hs-muted">
            Contact your Warden to correct protected profile details.
          </p>
        </Card>
        <Card>
          <ResourceForm
            title="Contact details"
            successMessage="Contact details saved."
            initial={{ phone: u.profile?.phone }}
            fields={[
              {
                name: "phone",
                label: "Phone number",
                type: "tel",
                maxLength: 20,
              },
            ]}
            onSave={async (body) =>
              setU(await api("/api/auth/profile/", { method: "PATCH", body }))
            }
          />
        </Card>
      </div>
    </>
  );
}
