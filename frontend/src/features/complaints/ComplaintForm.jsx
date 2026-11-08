'use client';
// Owner: Atiksh Gour | US-13 | Sprint 4 | Reviewer: Anvi Srinivas
import { useState } from 'react';
import { api } from '@/lib/api';

const categories = ['Electrical', 'Plumbing', 'Furniture', 'Cleaning', 'Other'];

export default function ComplaintForm({ onSaved }) {
  const [category, setCategory] = useState('');
  const [description, setDescription] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  async function submit(event) {
    event.preventDefault(); setBusy(true); setError(''); setNotice('');
    try {
      const result = await api('/api/complaints/', { method: 'POST', body: { category, description } });
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
        {categories.map((item) => <option key={item} value={item}>{item}</option>)}
      </select></p>
    <p><label htmlFor="complaint-description">Description</label><br />
      <textarea id="complaint-description" required maxLength={3000} rows={4} value={description}
        onChange={(event) => setDescription(event.target.value)} /></p>
    <button disabled={busy} type="submit">{busy ? 'Submitting…' : 'Submit complaint'}</button>
    {error && <p role="alert">{error}</p>}
    {notice && <p role="status">{notice}</p>}
  </form>;
}
