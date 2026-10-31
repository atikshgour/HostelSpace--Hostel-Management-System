'use client';
// Owner: Atiksh Gour | US-16 | Sprint 5 | Reviewer: Anvi Srinivas
import { useEffect, useState } from 'react';
import { getFees, initiateFee, verifyAttempt } from './api';

function loadCheckout() {
  if (window.Razorpay) return Promise.resolve();
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.onload = resolve;
    script.onerror = () => reject(new Error('Test checkout could not load.'));
    document.body.appendChild(script);
  });
}

export default function FeesPanel() {
  const [fees, setFees] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    let active = true;
    getFees().then((data) => { if (active) setFees(data.results); })
      .catch((err) => { if (active) setError(err.message); });
    return () => { active = false; };
  }, [revision]);
  function reload(clearError = true) { setFees(null); if (clearError) setError(''); setRevision((n) => n + 1); }
  async function pay(fee) {
    setBusy(true); setError('');
    try {
      await loadCheckout();
      const order = await initiateFee(fee.id);
      const checkout = new window.Razorpay({
        key: order.key_id, amount: order.amount, currency: order.currency,
        order_id: order.order_id, name: 'HostelSpace test payment',
        handler: async (result) => {
          try {
            await verifyAttempt(order.attempt_id, {
              payment_id: result.razorpay_payment_id, signature: result.razorpay_signature,
            });
          } catch (err) { setError(err.message); }
          finally { setBusy(false); reload(false); }
        },
        modal: { ondismiss: async () => {
          try { await verifyAttempt(order.attempt_id, { cancelled: true }); }
          catch (err) { setError(err.message); }
          finally { setBusy(false); reload(false); }
        } },
      });
      checkout.open();
    } catch (err) { setError(err.message); setBusy(false); reload(false); }
  }
  async function check(attemptId) {
    setBusy(true); setError('');
    try { await verifyAttempt(attemptId, {}); }
    catch (err) { setError(err.message); }
    finally { setBusy(false); reload(false); }
  }
  return <main className="hs-container">
    <h1>My hostel fees</h1>
    <p className="hs-muted">Test payments only. The server confirms the result before a fee is marked Paid.</p>
    <button onClick={() => reload()} disabled={busy}>Refresh fees</button>
    {!fees && !error && <p role="status">Loading fees…</p>}
    {error && <p role="alert">{error}</p>}
    {fees?.length === 0 && <p>No fees are currently due.</p>}
    <div className="hs-grid">{fees?.map((fee) => <section className="hs-card" key={fee.id}>
      <h2>{fee.description}</h2>
      <p>{fee.currency} {fee.amount} — {fee.status}</p>
      {fee.status === 'Unpaid' && <button disabled={busy} onClick={() => pay(fee)}>Pay in test mode</button>}
      {fee.status === 'Pending' && <p>Payment pending verification. Refresh to see the latest result.</p>}
      <h3>Attempts</h3>
      {fee.attempts.length ? <ul>{fee.attempts.map((item) =>
        <li key={item.id}>{item.status} — {new Date(item.created_at).toLocaleString()}
          {item.status === 'Pending' && <button disabled={busy} onClick={() => check(item.id)}>Verify result</button>}
        </li>)}</ul>
        : <p>No attempts yet.</p>}
    </section>)}</div>
  </main>;
}
