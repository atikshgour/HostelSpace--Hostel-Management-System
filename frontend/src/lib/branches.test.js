// US-22 | Transport, pagination, formatting and navigation decisions.
import {api, all, ApiError} from './api';
import {dateTime, money} from './format';
import {roleLabel, navGroup} from './roles';
import * as attendance from '../features/attendance/api';
import * as leave from '../features/leave/api';
import * as deviations from '../features/deviations/api';

const response = (body, status = 200) => ({ok: status < 400, status, json: async () => body});
beforeEach(() => {global.fetch = jest.fn(async () => response({csrfToken: 'test'}));});

test.each([attendance, leave, deviations])('domain transport enforces origin, CSRF and JSON errors %#', async (client) => {
  expect(new client.ApiError(400).fields).toEqual({});
  expect(new client.ApiError(400, {message: 'specific', fields: {x: 'bad'}}).message).toBe('specific');
  await expect(client.request('https://example.invalid')).rejects.toThrow(/same-origin/);
  await expect(client.request('//example.invalid')).rejects.toThrow(/same-origin/);
  fetch.mockResolvedValueOnce(response({}, 403));
  await expect(client.request('/api/x/', {method: 'POST'})).rejects.toThrow(/secure request/);
  fetch.mockResolvedValueOnce({ok: true, status: 200, json: async () => {throw Error('json');}});
  await expect(client.request('/api/x/', {method: 'PUT'})).rejects.toThrow(/secure request/);
  fetch.mockResolvedValueOnce(response({csrfToken: 't'})).mockResolvedValueOnce(response({message: 'Denied', fields: {id: 'bad'}}, 403));
  await expect(client.request('/api/x/', {method: 'POST', body: {id: 1}})).rejects.toMatchObject({message: 'Denied', fields: {id: 'bad'}});
  fetch.mockResolvedValueOnce({ok: true, json: async () => {throw Error('json');}});
  expect(await client.request('/api/x/')).toEqual({});
  await client.request('/api/x/', {method: 'POST'});
  expect(fetch.mock.calls.at(-1)[1]).not.toHaveProperty('body');
});

test('shared transport, failures and pagination keep credentials same-origin', async () => {
  expect(new ApiError(500).message).toMatch(/retry/);
  await expect(api('/other')).rejects.toThrow(/Same-origin/);
  fetch.mockResolvedValueOnce(response({}, 400));
  await expect(api('/api/x/', {method: 'POST'})).rejects.toMatchObject({status: 400});
  fetch.mockResolvedValueOnce(response({csrfToken: 't'})).mockResolvedValueOnce(response({message: 'Rejected'}, 400));
  await expect(api('/api/x/', {method: 'PATCH', body: {a: 1}})).rejects.toThrow('Rejected');
  fetch.mockResolvedValueOnce({ok: true, json: async () => {throw Error('json');}});
  expect(await api('/api/x/')).toEqual({});
  fetch.mockResolvedValueOnce(response({results: [1], next: 'http://localhost/api/x/?page=2'})).mockResolvedValueOnce(response({results: [2], next: null}));
  expect(await all('/api/x/')).toEqual([1, 2]);
  fetch.mockResolvedValueOnce(response({turnaround_days: 3}));
  expect(await all('/api/policy/')).toEqual({turnaround_days: 3});
  await api('/api/x/', {method: 'DELETE'});
  expect(fetch.mock.calls.at(-1)[1]).toMatchObject({credentials: 'same-origin', cache: 'no-store'});
});

test('domain endpoint helpers encode identifiers and optional filters', async () => {
  await attendance.getIdentity(); await attendance.listSessions(); await attendance.listSessions(2);
  await attendance.listAttendance(); await attendance.createSession({title: 'test'}); await attendance.submitAttendance({session: 1});
  await leave.getIdentity(); await leave.listLeaves(); await leave.listLeaves(2); await leave.getLeave('a/b');
  await leave.submitLeave({reason: 'test'}); await leave.decideLeave('a/b', {decision: 'Approved'});
  await deviations.getIdentity(); await deviations.listStudents(); await deviations.listStudents(2);
  await deviations.listRules(); await deviations.listRules(2); await deviations.listDeviations(); await deviations.listDeviations('a/b', 2);
  await deviations.getTotal('a/b', true); await deviations.getTotal('', false);
  await deviations.recordDeviation({student: 1}); await deviations.deactivateDeviation('a/b', 'corrected');
  expect(fetch.mock.calls.some(([url]) => url.includes('a%2Fb'))).toBe(true);
});

test('formatters and role menus handle defaults and all navigation categories', () => {
  expect(dateTime(null)).toBeTruthy(); expect(dateTime('2026-11-17')).toContain('2026');
  expect(money(2)).toContain('2'); expect(money(2, 'USD')).toContain('2');
  expect(roleLabel()).toBe(''); expect(roleLabel('DIRECTOR')).toBe('Admin'); expect(roleLabel('MESS_STAFF')).toBe('Mess Staff');
  for (const [path, group] of [['/dashboard','Overview'],['/profile','People & account'],['/leave','Requests & records'],['/attendance','Requests & records'],['/deviations','Requests & records'],['/complaints','Requests & records'],['/director','Administration'],['/mess','Hostel services']]) expect(navGroup(path)).toBe(group);
});
