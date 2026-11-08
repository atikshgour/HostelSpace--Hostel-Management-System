'use client';
// Owner: Atiksh Gour | US-14 | Sprint 4 | Reviewer: Anvi Srinivas
import { useEffect, useState } from 'react';
import { advanceComplaint, assignComplaint, listComplaints, listMaintenanceStaff } from './api';

function ComplaintCard({ complaint, canAssign, staff, onChanged }) {
  const [assignee, setAssignee] = useState(String(complaint.assigned_to || ''));
  const [remarks, setRemarks] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const next = { Open: 'In Progress', 'In Progress': 'Resolved' }[complaint.status];
  async function submit(event) {
    event.preventDefault();
    setBusy(true); setError(''); setSuccess('');
    try {
      const action = event.nativeEvent.submitter?.value;
      const updated = action === 'assign'
        ? await assignComplaint(complaint.id, { assigned_to: Number(assignee), remarks })
        : await advanceComplaint(complaint.id, {
          expected_status: complaint.status, status: next, remarks,
        });
      onChanged(updated); setRemarks(''); setSuccess('Complaint updated.');
    } catch (err) { setError(`${err.message} Reload complaints before retrying if the record changed.`); }
    finally { setBusy(false); }
  }
  return <article className="hs-card" aria-label={`Complaint ${complaint.id}`}>
    <h2>Complaint #{complaint.id} — {complaint.status}</h2>
    <p>{complaint.category_name} · Room {complaint.room}</p>
    <p>{complaint.description}</p>
    <p>Assigned staff: {complaint.assigned_to ? `#${complaint.assigned_to}` : 'Unassigned'}</p>
    {complaint.status !== 'Resolved' && <form onSubmit={submit}>
      <fieldset disabled={busy}>
        <legend>Update complaint</legend>
        {canAssign && <p><label htmlFor={`assignee-${complaint.id}`}>Maintenance Staff </label>
          <select id={`assignee-${complaint.id}`} value={assignee} onChange={(e) => setAssignee(e.target.value)}>
            <option value="">Select active staff</option>
            {staff.map((person) => <option key={person.id} value={person.id}>
              {[person.first_name, person.last_name].filter(Boolean).join(' ') || person.username}
            </option>)}
          </select></p>}
        <p><label htmlFor={`remarks-${complaint.id}`}>Remarks (required, up to 500 characters)</label><br />
          <textarea id={`remarks-${complaint.id}`} value={remarks} maxLength={500} required
            onChange={(e) => setRemarks(e.target.value)} rows={3} style={{ width: '100%' }} /></p>
        {canAssign && <button type="submit" value="assign"
          disabled={!assignee || Number(assignee) === complaint.assigned_to}>Assign staff</button>}{' '}
        {next && <button type="submit" value="progress" disabled={!complaint.assigned_to}>Mark {next}</button>}
        {busy && <p role="status">Saving…</p>}
      </fieldset>
    </form>}
    {error && <p role="alert">{error}</p>}
    {success && <p role="status">{success}</p>}
    <details><summary>History ({complaint.history.length})</summary>
      <ol>{complaint.history.map((event) => <li key={event.id}>
        <time dateTime={event.created_at}>{event.created_at}</time> · Actor #{event.actor}: {' '}
        {event.old_status || 'Created'} → {event.new_status}; {' '}
        staff {event.old_assigned_to || 'unassigned'} → {event.new_assigned_to || 'unassigned'}
        <p>{event.remarks}</p>
      </li>)}</ol>
    </details>
  </article>;
}

export default function ComplaintManagePanel() {
  const [data, setData] = useState(null);
  const [staff, setStaff] = useState([]);
  const [page, setPage] = useState(1);
  const [version, setVersion] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const result = await listComplaints(page);
        const people = result.can_assign ? await listMaintenanceStaff() : [];
        if (active) { setData(result); setStaff(people); setLoading(false); }
      } catch (err) { if (active) { setError(err.message); setLoading(false); } }
    }
    load();
    return () => { active = false; };
  }, [page, version]);
  function reload(nextPage = page) {
    setLoading(true); setError(''); setData(null); setPage(nextPage); setVersion((v) => v + 1);
  }
  function changed(complaint) {
    setData((current) => ({ ...current,
      results: current.results.map((item) => item.id === complaint.id ? complaint : item),
    }));
  }
  return <main className="hs-container">
    <h1>Manage maintenance complaints</h1>
    <p className="hs-muted">Director assignment and assigned Maintenance Staff progress.</p>
    <button onClick={() => reload()} disabled={loading}>Reload complaints</button>
    {loading && <p role="status">Loading complaints…</p>}
    {error && <p role="alert">{error}</p>}
    {!loading && data && <>
      {data.results.length === 0 && <p>No complaints available.</p>}
      {data.can_assign && staff.length === 0 && <p>No active Maintenance Staff available for assignment.</p>}
      <div className="hs-grid">{data.results.map((complaint) => <ComplaintCard
        key={`${complaint.id}-${version}`} complaint={complaint} canAssign={data.can_assign}
        staff={staff} onChanged={changed} />)}</div>
      <nav aria-label="Complaint pages">
        <button disabled={!data.previous} onClick={() => reload(page - 1)}>Previous</button>{' '}
        <span>Page {page}</span>{' '}
        <button disabled={!data.next} onClick={() => reload(page + 1)}>Next</button>
      </nav>
    </>}
  </main>;
}
