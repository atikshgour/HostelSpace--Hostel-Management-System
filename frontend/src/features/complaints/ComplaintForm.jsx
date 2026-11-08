'use client';
// Owner: Atiksh Gour | US-13 | Sprint 4 | Reviewer: Anvi Srinivas
import { useEffect, useState } from 'react';

export default function ComplaintForm({ onSaved }) {
  const [categories, setCategories] = useState([]);
  const [category, setCategory] = useState('');
  const [description, setDescription] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  useEffect(() => {
    let active = true;
    fetch('/api/complaint-categories/', { credentials: 'same-origin', cache: 'no-store' })
      .then(async (response) => {
        const data = await response.json();
        if (!response.ok) throw new Error(data.message || 'Unable to load categories.');
        return data.results;
      }).then((items) => { if (active) setCategories(items); })
      .catch((err) => { if (active) setError(err.message); });
    return () => { active = false; };
  }, []);
  async function submit(event) {
    event.preventDefault(); setBusy(true); setError(''); setNotice('');
    try {
      const csrf = document.cookie.split('; ').find((part) => part.startsWith('csrftoken='))?.slice(10) || '';
      const response = await fetch('/api/complaints/', { method: 'POST', credentials: 'same-origin',
        cache: 'no-store', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': decodeURIComponent(csrf) },
        body: JSON.stringify({ category: Number(category), description }) });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || 'Unable to submit complaint.');
      setDescription(''); setCategory(''); setNotice(`Complaint #${result.id} submitted.`);
      onSaved?.(result);
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }
  return <form className="hs-card" onSubmit={submit}>
    <h2>New maintenance complaint</h2>
    <p className="hs-muted">Your room comes from your student profile.</p>
    <p><label htmlFor="complaint-category">Category</label><br />
      <select id="complaint-category" required value={category} onChange={(event) => setCategory(event.target.value)}>
        <option value="">Select category</option>
        {categories.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
      </select></p>
    <p><label htmlFor="complaint-description">Description</label><br />
      <textarea id="complaint-description" required maxLength={2000} rows={4} value={description}
        onChange={(event) => setDescription(event.target.value)} /></p>
    <button disabled={busy || !categories.length} type="submit">{busy ? 'Submitting…' : 'Submit complaint'}</button>
    {error && <p role="alert">{error}</p>}
    {notice && <p role="status">{notice}</p>}
  </form>;
}
