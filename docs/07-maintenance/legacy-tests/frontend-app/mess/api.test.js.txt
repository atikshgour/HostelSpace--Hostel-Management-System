// Owner: Atiksh Gour | US-15 | Sprint 5 | Reviewer: Anvi Srinivas
import { getMessManagement, getMyMess, saveAllocation, saveCoupon } from '../../src/features/mess/api';
beforeEach(() => { global.fetch = jest.fn(); });
afterEach(() => { delete global.fetch; });
const reply = (data, ok = true) => ({ ok, json: async () => data });

test('personal records use the uncached same-origin session', async () => {
  fetch.mockResolvedValue(reply({ allocation: null, coupons: [] }));
  await getMyMess();
  expect(fetch).toHaveBeenCalledWith('/api/mess/', { method: 'GET', credentials: 'same-origin', cache: 'no-store' });
});

test('management follows every page of each staff-only list', async () => {
  fetch.mockImplementation(async (path) => reply({
    results: [{ id: path.endsWith('page=2') ? 2 : 1 }],
    next: path.endsWith('page=1') ? 'next-page' : null,
  }));
  const data = await getMessManagement();
  expect(fetch).toHaveBeenCalledTimes(6);
  expect(data.students).toEqual([{ id: 1 }, { id: 2 }]);
  expect(data.allocations).toHaveLength(2);
  expect(data.coupons).toHaveLength(2);
});

test('create and update use CSRF and surface field errors', async () => {
  document.cookie = 'csrftoken=synthetic-token';
  fetch.mockResolvedValueOnce(reply({ id: 1 }));
  await saveAllocation(undefined, { student: 3 });
  expect(fetch.mock.calls[0][1]).toMatchObject({ method: 'POST', headers: {
    'Content-Type': 'application/json', 'X-CSRFToken': 'synthetic-token',
  } });
  fetch.mockResolvedValueOnce(reply({ message: 'Check fields.', fields: { code: ['Required.'] } }, false));
  await expect(saveCoupon(1, { expected_version: 1 })).rejects.toThrow('Check fields. code: Required.');
  expect(fetch.mock.calls[1][0]).toBe('/api/mess/coupons/1/');
  expect(fetch.mock.calls[1][1].method).toBe('PATCH');
});
