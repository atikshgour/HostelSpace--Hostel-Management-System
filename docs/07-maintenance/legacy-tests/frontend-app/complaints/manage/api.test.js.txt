// Owner: Atiksh Gour | US-14 | Sprint 4 | Reviewer: Anvi Srinivas
import { advanceComplaint, assignComplaint, listComplaints, listMaintenanceStaff } from '../../../src/features/complaints/api';

beforeEach(() => { global.fetch = jest.fn(); });
afterEach(() => { delete global.fetch; });
function reply(data, ok = true) {
  return { ok, json: async () => data };
}

test('reads use the same-origin session without caching; staff dropdown loads every page', async () => {
  fetch.mockResolvedValueOnce(reply({ results: [], can_assign: true }));
  await listComplaints(2);
  expect(fetch).toHaveBeenCalledWith('/api/complaints/manage/?page=2', {
    credentials: 'same-origin', cache: 'no-store',
  });
  fetch.mockResolvedValueOnce(reply({ results: [{ id: 3 }], next: '/api/maintenance-staff/?page=2' }))
    .mockResolvedValueOnce(reply({ results: [{ id: 4 }], next: null }));
  expect(await listMaintenanceStaff()).toEqual([{ id: 3 }, { id: 4 }]);
});

test('writes include CSRF and server error fields are displayed', async () => {
  document.cookie = 'csrftoken=synthetic-csrf';
  fetch.mockResolvedValueOnce(reply({ id: 7 }));
  await assignComplaint(7, { assigned_to: 3, remarks: 'Synthetic' });
  expect(fetch.mock.calls[0][1]).toMatchObject({ method: 'POST', cache: 'no-store',
    headers: { 'X-CSRFToken': 'synthetic-csrf', 'Content-Type': 'application/json' } });
  fetch.mockResolvedValueOnce(reply({ message: 'Invalid input.', fields: { remarks: ['Required.'] } }, false));
  await expect(advanceComplaint(7, {})).rejects.toThrow('Invalid input. remarks: Required.');
});
