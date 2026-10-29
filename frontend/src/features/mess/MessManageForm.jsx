'use client';
// Owner: Atiksh Gour | US-15 | Sprint 5 | Reviewer: Anvi Srinivas
import { useId, useState } from 'react';
import { saveAllocation, saveCoupon } from './api';

export default function MessManageForm({ kind, record, students = [], allocations = [], onSaved }) {
  const id = useId();
  const isCoupon = kind === 'coupon';
  const [target, setTarget] = useState('');
  const [name, setName] = useState(record?.[isCoupon ? 'code' : 'mess_name'] || '');
  const [from, setFrom] = useState(record?.valid_from || '');
  const [until, setUntil] = useState(record?.valid_until || '');
  const [active, setActive] = useState(record?.is_active ?? true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const label = isCoupon ? 'Coupon' : 'Allocation';
  async function submit(event) {
    event.preventDefault();
    setError(''); setSuccess('');
    if (until < from) { setError('Valid until must be on or after valid from.'); return; }
    if (!name.trim()) { setError(isCoupon ? 'Enter a coupon code.' : 'Enter a mess name.'); return; }
    setBusy(true);
    try {
      const data = { [isCoupon ? 'code' : 'mess_name']: name.trim(), valid_from: from, valid_until: until, is_active: active,
        ...(record ? { expected_version: record.version } : { [isCoupon ? 'allocation' : 'student']: Number(target) }) };
      const result = await (isCoupon ? saveCoupon : saveAllocation)(record?.id, data);
      onSaved(kind, result); setSuccess(`${label} saved.`);
      if (!record) { setName(''); setTarget(''); setFrom(''); setUntil(''); setActive(true); }
    } catch (err) { setError(`${err.message} Reload records if another staff member changed this record.`); }
    finally { setBusy(false); }
  }
  return <form className="hs-card" onSubmit={submit} aria-label={record ? `Edit ${label.toLowerCase()} ${record.id}` : `Create ${label.toLowerCase()}`}>
    <h2>{record ? `${label} #${record.id}` : `Create ${label.toLowerCase()}`}</h2>
    {record && <p>{isCoupon ? `Allocation #${record.allocation}` : `Student #${record.student}`} · Version {record.version}</p>}
    <fieldset disabled={busy}>
      <legend>{label} details</legend>
      {!record && <p><label htmlFor={`${id}-target`}>{isCoupon ? 'Allocation' : 'Student'} </label>
        <select id={`${id}-target`} required value={target} onChange={(event) => setTarget(event.target.value)}>
          <option value="">Select {isCoupon ? 'allocation' : 'student'}</option>
          {isCoupon ? allocations.map((item) => <option key={item.id} value={item.id}>
            #{item.id}: {item.mess_name} — Student #{item.student}
          </option>) : students.map((item) => <option key={item.id} value={item.id}>
            {item.username} {[item.first_name, item.last_name].filter(Boolean).join(' ')}
          </option>)}
        </select></p>}
      <p><label htmlFor={`${id}-name`}>{isCoupon ? 'Coupon code' : 'Mess name'} </label>
        <input id={`${id}-name`} required maxLength={isCoupon ? 80 : 100} value={name} onChange={(event) => setName(event.target.value)} /></p>
      <p><label htmlFor={`${id}-from`}>Valid from </label>
        <input id={`${id}-from`} type="date" required value={from} onChange={(event) => setFrom(event.target.value)} /></p>
      <p><label htmlFor={`${id}-until`}>Valid until </label>
        <input id={`${id}-until`} type="date" required min={from} value={until} onChange={(event) => setUntil(event.target.value)} /></p>
      <p><label><input type="checkbox" checked={active} onChange={(event) => setActive(event.target.checked)} /> Active</label></p>
      <button type="submit">{busy ? 'Saving…' : `Save ${label.toLowerCase()}`}</button>
    </fieldset>
    {error && <p role="alert">{error}</p>}
    {success && <p role="status">{success}</p>}
  </form>;
}
