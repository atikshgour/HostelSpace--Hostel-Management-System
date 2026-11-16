"use client";
import { useState } from "react";
import {
  useResource,
  ErrorMessage,
  ResourceForm,
} from "@/components/ui/AppShell";
import Card from "@/components/ui/Card";
import PageHeader from "@/components/ui/PageHeader";
import Button from "@/components/ui/Button";
import StatusBadge from "@/components/ui/StatusBadge";
import Dialog from "@/components/ui/Dialog";
import { api } from "@/lib/api";
export default function ContentEditor() {
  const { data, error, refresh } = useResource([
    "/api/information/",
    "/api/rules/",
  ]);
  const [editing, setEditing] = useState(null),
    [rule, setRule] = useState(false),
    [open, setOpen] = useState(false);
  const fields = rule
    ? [
        { name: "title", label: "Rule title" },
        { name: "body", label: "Rule text", type: "textarea", optional: true },
        {
          name: "weightage",
          label: "Weightage",
          type: "number",
          min: 0,
          step: ".01",
        },
        { name: "active", label: "Active", type: "checkbox" },
      ]
    : [
        {
          name: "kind",
          label: "Content type",
          options: [
            { value: "notice", label: "Announcement" },
            { value: "information", label: "Hostel information" },
            { value: "contact", label: "Contact" },
          ],
        },
        { name: "title", label: "Title" },
        { name: "body", label: "Content", type: "textarea" },
        {
          name: "starts_at",
          label: "Visible from",
          type: "datetime-local",
          nullable: true,
          optional: true,
        },
        {
          name: "ends_at",
          label: "Visible until",
          type: "datetime-local",
          nullable: true,
          optional: true,
        },
        { name: "active", label: "Active", type: "checkbox" },
      ];
  return (
    <>
      <PageHeader
        title="Announcements & rules"
        description="Publish hostel announcements, maintain contacts and explain the rules clearly."
      >
        <Button
          variant="primary"
          onClick={() => {
            setEditing(null);
            setOpen(true);
          }}
        >
          + {rule ? "Create rule" : "Publish announcement"}
        </Button>
      </PageHeader>
      <ErrorMessage error={error} />
      <div className="hs-actions" style={{ marginBottom: 20 }}>
        <Button
          onClick={() => {
            setRule(false);
            setEditing(null);
          }}
        >
          Announcements & contacts
        </Button>
        <Button
          onClick={() => {
            setRule(true);
            setEditing(null);
          }}
        >
          Rules
        </Button>
      </div>
      <div>
        {open ? (
          <Dialog
            title={
              editing
                ? "Edit published record"
                : rule
                  ? "Create rule"
                  : "Publish an announcement"
            }
            onClose={() => setOpen(false)}
          >
            <ResourceForm
              key={`${rule}-${editing?.id || "new"}`}
              title={
                editing
                  ? "Edit record"
                  : rule
                    ? "Create rule"
                    : "Publish content"
              }
              initial={
                editing
                  ? {
                      ...editing,
                      starts_at: editing.starts_at
                        ? new Date(
                            new Date(editing.starts_at).getTime() -
                              new Date(editing.starts_at).getTimezoneOffset() *
                                60000,
                          )
                            .toISOString()
                            .slice(0, 16)
                        : "",
                      ends_at: editing.ends_at
                        ? new Date(
                            new Date(editing.ends_at).getTime() -
                              new Date(editing.ends_at).getTimezoneOffset() *
                                60000,
                          )
                            .toISOString()
                            .slice(0, 16)
                        : "",
                    }
                  : { active: true, kind: "notice" }
              }
              fields={fields}
              onCancel={editing ? () => setEditing(null) : null}
              onSave={async (body) => {
                for (const k of ["starts_at", "ends_at"])
                  if (body[k]) body[k] = new Date(body[k]).toISOString();
                await api(
                  `/api/${rule ? "rules" : "information"}/${editing ? editing.id + "/" : ""}`,
                  { method: editing ? "PATCH" : "POST", body },
                );
                setOpen(false);
                setEditing(null);
                refresh();
              }}
            />
          </Dialog>
        ) : null}
        <Card>
          <h2>Published records</h2>
          {(data?.[rule ? 1 : 0] || []).map((x) => (
            <div className="hs-list-item" key={x.id}>
              <div className="hs-row">
                <strong>{x.title}</strong>
                <StatusBadge>{x.active ? "Active" : "Inactive"}</StatusBadge>
              </div>
              <p className="hs-muted">
                {rule ? `Weightage ${x.weightage}` : x.kind}
              </p>
              <Button
                onClick={() => {
                  setEditing(x);
                  setOpen(true);
                }}
              >
                Edit
              </Button>
            </div>
          ))}
        </Card>
      </div>
    </>
  );
}
