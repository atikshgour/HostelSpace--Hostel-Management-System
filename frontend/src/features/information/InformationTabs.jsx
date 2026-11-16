"use client";
import { useState } from "react";
import { useResource, ErrorMessage } from "@/components/ui/AppShell";
import Card from "@/components/ui/Card";
import PageHeader from "@/components/ui/PageHeader";
import EmptyState from "@/components/ui/EmptyState";
import Button from "@/components/ui/Button";
export default function InformationTabs() {
  const { data, error } = useResource(["/api/information/", "/api/rules/"]);
  const [tab, setTab] = useState("notice");
  return (
    <>
      <PageHeader
        title="Announcements & information"
        description="Updates, contacts and rules from your hostel administration."
      />
      <div className="hs-tabs">
        {[
          ["notice", "Announcements"],
          ["information", "Hostel information"],
          ["contact", "Contacts"],
          ["rules", "Rules"],
        ].map(([k, l]) => (
          <Button
            key={k}
            variant={tab === k ? "primary" : ""}
            onClick={() => setTab(k)}
          >
            {l}
          </Button>
        ))}
      </div>
      <ErrorMessage error={error} />
      {!data && !error ? <p role="status">Loading information…</p> : null}
      <div className="hs-stack">
        {(tab === "rules"
          ? data?.[1]
          : data?.[0]?.filter((x) => x.kind === tab)
        )?.map((x) => (
          <Card key={x.id}>
            <h2>{x.title}</h2>
            <p style={{ whiteSpace: "pre-wrap" }}>{x.body}</p>
            {tab === "rules" ? (
              <p className="hs-muted">
                Rule #{x.id} · Weightage {x.weightage}
              </p>
            ) : null}
          </Card>
        ))}
      </div>
      {data &&
      !(tab === "rules" ? data[1] : data[0].filter((x) => x.kind === tab))
        .length ? (
        <EmptyState>No current records.</EmptyState>
      ) : null}
    </>
  );
}
