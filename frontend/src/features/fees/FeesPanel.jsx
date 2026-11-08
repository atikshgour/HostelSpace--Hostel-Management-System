"use client";
import { useState } from "react";
import { api } from "@/lib/api";
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
import { money, dateTime } from "@/lib/format";
async function loadCheckout() {
  if (window.Razorpay) return;
  await new Promise((resolve, reject) => {
    const s = document.createElement("script");
    s.src = "https://checkout.razorpay.com/v1/checkout.js";
    s.onload = resolve;
    s.onerror = () => reject(new Error("Unable to load sandbox checkout."));
    document.body.append(s);
  });
}
export default function FeesPanel() {
  const user = useIdentity(),
    director = ["DIRECTOR", "WARDEN"].includes(user.role);
  const { data, error, refresh } = useResource([
    "/api/fees/",
    "/api/payments/attempts/",
    director ? "/api/choices/users/" : null,
  ]);
  const [failure, setFailure] = useState(null),
    [attempt, setAttempt] = useState(null),
    [busy, setBusy] = useState(false),
    [message, setMessage] = useState("");
  async function begin(fee) {
    setBusy(true);
    setFailure(null);
    try {
      const a = await api("/api/payments/initiate/", {
        method: "POST",
        body: { fee },
      });
      refresh();
      if (a.provider === "simulation") {
        setAttempt(a);
        return;
      }
      await loadCheckout();
      const checkout = new window.Razorpay({
        key: a.checkout_key,
        order_id: a.order_id,
        amount: Math.round(Number(a.amount) * 100),
        currency: a.currency,
        name: "HostelSpace · TEST",
        description: "Sandbox hostel fee payment",
        handler: async (r) => {
          try {
            await api("/api/payments/verify/", {
              method: "POST",
              body: {
                attempt: a.id,
                payment_id: r.razorpay_payment_id,
                signature: r.razorpay_signature,
              },
            });
            setMessage("Sandbox payment verified by the server.");
            refresh();
          } catch (e) {
            setFailure(e);
          }
        },
        modal: {
          ondismiss: () => {
            setMessage(
              "Checkout closed. No success was verified; the attempt remains Pending.",
            );
            refresh();
          },
        },
      });
      checkout.open();
    } catch (e) {
      setFailure(e);
    } finally {
      setBusy(false);
    }
  }
  async function simulate(outcome) {
    setBusy(true);
    setFailure(null);
    try {
      await api("/api/payments/simulate/", {
        method: "POST",
        body: { attempt: attempt.id, outcome },
      });
      setMessage(`Local simulation: ${outcome}. No real payment was made.`);
      setAttempt(null);
      refresh();
    } catch (e) {
      setFailure(e);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <PageHeader
        title="Fees & payments"
        description="Fee balances and retained payment-attempt history. Live payments are not supported."
      />
      <ErrorMessage error={error || failure} />
      {message ? (
        <p role="status" className="hs-notice">
          {message}
        </p>
      ) : null}
      {director ? (
        <Card>
          <ResourceForm
            title="Create fee due"
            fields={[
              {
                name: "student",
                label: "Student",
                options: (data?.[2] || []).map((x) => ({
                  value: x.id,
                  label: x.name,
                })),
              },
              { name: "title", label: "Fee title" },
              {
                name: "amount",
                label: "Amount",
                type: "number",
                min: ".01",
                step: ".01",
              },
              { name: "currency", label: "Currency", options: ["INR"] },
              { name: "due_date", label: "Due date", type: "date" },
            ]}
            onSave={async (body) => {
              await api("/api/fees/", { method: "POST", body });
              refresh();
            }}
          />
        </Card>
      ) : null}
      <div className="hs-stack" style={{ marginTop: 24 }}>
        {(data?.[0] || []).map((x) => (
          <Card key={x.id}>
            <div className="hs-row">
              <div>
                <h2>{x.title}</h2>
                <p className="hs-stat">{money(x.amount, x.currency)}</p>
                <p className="hs-muted">
                  Due {x.due_date}
                  {director ? ` · ${x.student_name || "Student"}` : ""}
                </p>
              </div>
              <div className="hs-stack">
                <StatusBadge>{x.status}</StatusBadge>
                {!director && x.status !== "Paid" ? (
                  <Button
                    variant="primary"
                    disabled={busy}
                    onClick={() => begin(x.id)}
                  >
                    Open test checkout
                  </Button>
                ) : null}
              </div>
            </div>
          </Card>
        ))}
        <Card>
          <h2>Payment history</h2>
          <DataTable
            headers={["Attempt", "Fee", "Amount", "Mode", "Status", "Created"]}
            rows={(data?.[1] || []).map((x) => [
              x.id.slice(0, 8),
              x.fee,
              money(x.amount, x.currency),
              x.provider === "simulation"
                ? "Local simulation"
                : "Razorpay TEST",
              <StatusBadge key="status">{x.status}</StatusBadge>,
              dateTime(x.created_at),
            ])}
          />
          {data && !data[1].length ? (
            <p className="hs-empty">No payment attempts.</p>
          ) : null}
        </Card>
      </div>
      {attempt ? (
        <div className="hs-modal">
          <section
            className="hs-card"
            role="dialog"
            aria-modal="true"
            aria-label="Local payment simulation"
          >
            <h2>LOCAL PAYMENT SIMULATION</h2>
            <p className="hs-notice">
              No funds, card details or real payments. For coursework
              demonstration only; obtain faculty approval before presenting it
              as payment acceptance evidence.
            </p>
            <p>{money(attempt.amount, attempt.currency)}</p>
            <div className="hs-actions">
              {["Success", "Failed", "Cancelled"].map((x) => (
                <Button disabled={busy} key={x} onClick={() => simulate(x)}>
                  Simulate {x.toLowerCase()}
                </Button>
              ))}
            </div>
          </section>
        </div>
      ) : null}
    </>
  );
}
