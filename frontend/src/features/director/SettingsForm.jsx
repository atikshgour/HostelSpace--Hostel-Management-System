"use client";
import { api } from "@/lib/api";
import {
  useResource,
  ErrorMessage,
  ResourceForm,
} from "@/components/ui/AppShell";
import Card from "@/components/ui/Card";
import PageHeader from "@/components/ui/PageHeader";
export default function SettingsForm() {
  const { data, error, refresh } = useResource(["/api/director/settings/"]);
  return (
    <>
      <PageHeader
        title="Portal settings"
        description="Maintain the approved site title and support contact."
      />
      <ErrorMessage error={error} />
      <div className="hs-grid">
        <Card>
          <ResourceForm
            title="Update setting"
            fields={[
              {
                name: "key",
                label: "Setting",
                options: [
                  { value: "site_title", label: "Site title" },
                  { value: "support_contact", label: "Support contact" },
                ],
              },
              { name: "value", label: "Value" },
            ]}
            onSave={async (body) => {
              await api("/api/director/settings/", { method: "POST", body });
              refresh();
            }}
          />
        </Card>
        <Card>
          <h2>Current values</h2>
          {(data?.[0] || []).map((x) => (
            <div key={x.key} className="hs-list-item">
              <h3>{x.key.replaceAll("_", " ")}</h3>
              <p>{x.value}</p>
            </div>
          ))}
        </Card>
      </div>
    </>
  );
}
