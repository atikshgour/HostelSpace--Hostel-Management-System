"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Alert, Button, EmptyState, Loading } from "@/components/ui";

// Role -> items shown on dashboard (UI convenience only; server enforces access).
const LINKS = { "My profile": "/profile", "Users & roles": "/director/users" };

const MENU = {
  student: ["My profile", "Notices & rules", "Study room status", "Laundry", "Leave", "Attendance", "Complaints", "Mess", "Fees"],
  warden: ["Leave requests", "Attendance", "Deviation records"],
  chief_warden: ["Wardens", "Escalated cases"],
  director: ["Users & roles", "Hostel information", "Reports"],
  maintenance: ["Assigned complaints"],
  mess: ["Mess allocation", "Coupons"],
  laundry: ["Laundry days", "Handover & collection"],
};

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/api/auth/me/")
      .then(setUser)
      .catch((e) => {
        if (e.status === 401) router.replace("/login");
        else setError("Could not load your dashboard. Please try again.");
      });
  }, [router]);

  async function signOut() {
    await api("/api/auth/logout/", { method: "POST" }).catch(() => {});
    router.replace("/login");
  }

  if (error) return <main className="p-8"><Alert type="error">{error}</Alert></main>;
  if (!user) return <main className="p-8"><Loading /></main>;

  const items = MENU[user.role] || [];
  return (
    <main className="p-8">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Welcome, {user.name}</h1>
        <Button variant="secondary" onClick={signOut}>Sign out</Button>
      </div>
      <p className="mt-1 text-sm" style={{ color: "var(--hs-muted)" }}>Role: {user.role}</p>
      <div className="mt-6">
        {items.length === 0 ? (
          <EmptyState title="Nothing here yet" message="No services are available for your role." />
        ) : (
          <ul className="grid gap-3 sm:grid-cols-3">
            {items.map((i) => (
              <li key={i} className="hs-card">
                {LINKS[i] ? <a href={LINKS[i]} className="underline">{i}</a> : i}
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  );
}
