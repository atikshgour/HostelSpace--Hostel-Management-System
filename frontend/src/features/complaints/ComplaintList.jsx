'use client';
// Owner: Atiksh Gour | US-13/14 | Sprint 4 | Reviewer: Anvi Srinivas
import { useEffect, useState } from 'react';
import ComplaintForm from './ComplaintForm';

export default function ComplaintList() {
  const [page, setPage] = useState(1);
  const [revision, setRevision] = useState(0);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    fetch(`/api/complaints/?page=${page}`, { credentials: 'same-origin', cache: 'no-store' })
      .then(async (response) => {
        const result = await response.json();
        if (!response.ok) throw new Error(result.message || 'Unable to load complaints.');
        return result;
      }).then((result) => { if (active) setData(result); })
      .catch((err) => { if (active) setError(err.message); });
    return () => { active = false; };
  }, [page, revision]);
  function reload(nextPage = page) {
    setData(null); setError(''); setPage(nextPage); setRevision((value) => value + 1);
  }
  return <main className="hs-container">
    <h1>My maintenance complaints</h1>
    <ComplaintForm onSaved={() => reload(1)} />
    <section aria-label="Complaint history">
      <h2>Submitted complaints</h2>
      <button onClick={() => reload()}>Refresh</button>
      {!data && !error && <p role="status">Loading complaints…</p>}
      {error && <p role="alert">{error}</p>}
      {data?.results.length === 0 && <p>No complaints submitted yet.</p>}
      <div className="hs-grid">{data?.results.map((complaint) =>
        <article className="hs-card" key={complaint.id}>
          <h3>Complaint #{complaint.id} — {complaint.status}</h3>
          <p>{complaint.category_name} · Room {complaint.room}</p>
          <p>{complaint.description}</p>
          <details><summary>History ({complaint.history.length})</summary>
            <ol>{complaint.history.map((item) => <li key={item.id}>
              <time dateTime={item.created_at}>{new Date(item.created_at).toLocaleString()}</time>
              {' · '}{item.old_status || 'Created'} → {item.new_status}; {item.remarks}
            </li>)}</ol>
          </details>
        </article>)}</div>
      {data && <nav aria-label="Complaint pages">
        <button disabled={!data.previous} onClick={() => reload(page - 1)}>Previous</button>
        {' '}Page {page}{' '}
        <button disabled={!data.next} onClick={() => reload(page + 1)}>Next</button>
      </nav>}
    </section>
  </main>;
}
