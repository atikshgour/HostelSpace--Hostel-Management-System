'use client';
// Owner: Atiksh Gour | US-15 | Sprint 5 | Reviewer: Anvi Srinivas
import { useEffect, useState } from 'react';
import { getMessManagement, getMyMess } from './api';
import MessManageForm from './MessManageForm';

export default function MessPanel({ management = false }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [revision, setRevision] = useState(0);
  const [notice, setNotice] = useState('');
  useEffect(() => {
    let active = true;
    (management ? getMessManagement() : getMyMess()).then((result) => {
      if (active) { setData(result); setLoading(false); }
    }).catch((err) => { if (active) { setError(err.message); setLoading(false); } });
    return () => { active = false; };
  }, [management, revision]);
  function reload() {
    setData(null); setError(''); setLoading(true); setNotice(''); setRevision((value) => value + 1);
  }
  function saved(kind, record) {
    const key = kind === 'coupon' ? 'coupons' : 'allocations';
    setData((current) => ({ ...current, [key]: current[key].some((item) => item.id === record.id)
      ? current[key].map((item) => item.id === record.id ? record : item) : [...current[key], record] }));
    setNotice(`${kind === 'coupon' ? 'Coupon' : 'Allocation'} saved.`);
  }
  return <main className="hs-container">
    <h1>{management ? 'Manage mess allocations and coupons' : 'My mess and coupons'}</h1>
    <p className="hs-muted">Validity dates include both endpoints and use Asia/Kolkata.</p>
    <button onClick={reload} disabled={loading}>Reload records</button>
    {loading && <p role="status">Loading mess records…</p>}
    {error && <p role="alert">{error}</p>}
    {notice && <p role="status">{notice}</p>}
    {!loading && data && (management ? <>
      {data.students.length === 0 && <p>No active students available.</p>}
      <div className="hs-grid">
        <MessManageForm kind="allocation" students={data.students} onSaved={saved} />
        <MessManageForm kind="coupon" allocations={data.allocations} onSaved={saved} />
      </div>
      <h2>Existing allocations</h2>
      {data.allocations.length === 0 && <p>No allocations recorded.</p>}
      <div className="hs-grid">{data.allocations.map((item) => <MessManageForm key={`allocation-${item.id}-${item.version}`}
        kind="allocation" record={item} onSaved={saved} />)}</div>
      <h2>Existing coupons</h2>
      {data.coupons.length === 0 && <p>No coupons recorded.</p>}
      <div className="hs-grid">{data.coupons.map((item) => <MessManageForm key={`coupon-${item.id}-${item.version}`}
        kind="coupon" record={item} onSaved={saved} />)}</div>
    </> : <>
      <p>Current as of {data.as_of} ({data.timezone}).</p>
      <section className="hs-card"><h2>Assigned mess</h2>
        {data.allocation ? <>
          <p>{data.allocation.mess_name}</p>
          <p>Valid {data.allocation.valid_from} through {data.allocation.valid_until}</p>
        </> : <p>No current active mess allocation.</p>}
      </section>
      <section className="hs-card"><h2>Valid coupons</h2>
        {data.coupons.length ? <ul>{data.coupons.map((coupon) => <li key={coupon.id}>
          <strong>{coupon.code}</strong> — Valid {coupon.valid_from} through {coupon.valid_until}
        </li>)}</ul> : <p>No currently valid coupons.</p>}
      </section>
    </>)}
  </main>;
}
