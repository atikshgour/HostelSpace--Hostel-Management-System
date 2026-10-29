// Owner: Atiksh Gour | US-15 | Sprint 5 | Reviewer: Anvi Srinivas
// Scoped session/CSRF adapter until the shared US-01 client is implemented.
async function request(path, method = 'GET', body) {
  const token = typeof document === 'undefined' ? '' : document.cookie.split('; ')
    .find((cookie) => cookie.startsWith('csrftoken='))?.slice(10);
  const response = await fetch(`/api/mess/${path}`, {
    method, credentials: 'same-origin', cache: 'no-store',
    ...(body ? { headers: { 'Content-Type': 'application/json', 'X-CSRFToken': decodeURIComponent(token || '') },
      body: JSON.stringify(body) } : {}),
  });
  const data = await response.json();
  if (!response.ok) {
    const fields = Object.entries(data.fields || {}).map(([field, errors]) =>
      `${field}: ${Array.isArray(errors) ? errors.join(' ') : errors}`).join(' ');
    throw new Error([data.message || 'Request failed.', fields].filter(Boolean).join(' '));
  }
  return data;
}

async function allPages(path) {
  const rows = [];
  let page = 1;
  let data;
  do {
    data = await request(`${path}?page=${page++}`);
    rows.push(...data.results);
  } while (data.next);
  return rows;
}

export const getMyMess = () => request('');
export async function getMessManagement() {
  const [students, allocations, coupons] = await Promise.all([
    allPages('students/'), allPages('allocations/'), allPages('coupons/'),
  ]);
  return { students, allocations, coupons };
}
export const saveAllocation = (id, body) => request(`allocations/${id ? `${id}/` : ''}`, id ? 'PATCH' : 'POST', body);
export const saveCoupon = (id, body) => request(`coupons/${id ? `${id}/` : ''}`, id ? 'PATCH' : 'POST', body);
