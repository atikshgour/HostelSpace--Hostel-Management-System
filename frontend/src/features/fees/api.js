// Owner: Atiksh Gour | US-16 | Sprint 5 | Reviewer: Anvi Srinivas
async function request(path, method = 'GET', body) {
  const token = typeof document === 'undefined' ? '' : document.cookie.split('; ')
    .find((cookie) => cookie.startsWith('csrftoken='))?.slice(10);
  const response = await fetch(`/api/${path}`, {
    method, credentials: 'same-origin', cache: 'no-store',
    ...(body ? { headers: { 'Content-Type': 'application/json', 'X-CSRFToken': decodeURIComponent(token || '') },
      body: JSON.stringify(body) } : {}),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.message || data.detail || 'Payment request failed.');
  return data;
}
export const getFees = () => request('fees/');
export const initiateFee = (id) => request(`fees/${id}/initiate/`, 'POST', {});
export const verifyAttempt = (id, body) => request(`payment-attempts/${id}/verify/`, 'POST', body);
