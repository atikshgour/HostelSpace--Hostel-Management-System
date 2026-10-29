// Owner: Atiksh Gour | US-14 | Sprint 4 | Reviewer: Anvi Srinivas
// Uses the Django session; no client token store or separate authentication.
async function request(path, body) {
  const csrf = typeof document === 'undefined' ? '' : document.cookie.split('; ')
    .find((cookie) => cookie.startsWith('csrftoken='))?.slice('csrftoken='.length);
  const response = await fetch(path, {
    credentials: 'same-origin', cache: 'no-store',
    ...(body ? { method: 'POST', headers: { 'Content-Type': 'application/json',
      'X-CSRFToken': decodeURIComponent(csrf || '') }, body: JSON.stringify(body) } : {}),
  });
  const data = await response.json();
  if (!response.ok) {
    const fields = Object.entries(data.fields || {}).map(([key, errors]) =>
      `${key}: ${Array.isArray(errors) ? errors.join(' ') : errors}`).join(' ');
    throw new Error([data.message || 'Request failed.', fields].filter(Boolean).join(' '));
  }
  return data;
}

export const listComplaints = (page = 1) => request(`/api/complaints/manage/?page=${page}`);
export async function listMaintenanceStaff() {
  const staff = [];
  let page = 1;
  let data;
  do {
    data = await request(`/api/maintenance-staff/?page=${page++}`);
    staff.push(...data.results);
  } while (data.next);
  return staff;
}
export const assignComplaint = (id, body) => request(`/api/complaints/${id}/assign/`, body);
export const advanceComplaint = (id, body) => request(`/api/complaints/${id}/progress/`, body);
