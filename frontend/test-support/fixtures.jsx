// US-22/23 | Synthetic component fixtures. Only browser transport/navigation mocked.
import { fireEvent, render, screen } from '@testing-library/react';
import AppShell from '@/components/ui/AppShell';

jest.mock('next/navigation', () => {
  const router = {replace: jest.fn(), refresh: jest.fn()};
  return {useRouter: () => router, usePathname: () => global.__testPath || '/dashboard'};
});

export const stamp = '2026-11-17T10:00:00Z';
export const person = {id: 1, name: 'Synthetic Student', username: 'student', role: 'STUDENT', is_active: true,
  profile: {srn: 'TEST-001', room: '101', hostel: 'A', assigned_warden: 2}};
export const users = [person, {id: 2, name: 'Warden', username: 'warden', role: 'WARDEN', is_active: true},
  {id: 3, name: 'Chief', username: 'chief', role: 'CHIEF_WARDEN', is_active: true},
  {id: 4, name: 'Inactive Staff', username: 'staff', role: 'MESS_STAFF', is_active: false}];
export function installApi(role = 'STUDENT', routes = {}, path = '/dashboard') {
  global.__testPath = path;
  window.matchMedia = jest.fn(() => ({matches: false, addEventListener: jest.fn(), removeEventListener: jest.fn()}));
  global.fetch = jest.fn(async (url, options = {}) => {
    const method = options.method || 'GET';
    if (url === '/api/auth/me/') return reply({...person, role});
    if (url === '/api/auth/csrf/') return reply({csrfToken: 'synthetic'});
    let value = routes[`${method} ${url}`] ?? routes[url];
    if (typeof value === 'function') value = await value(options);
    if (value instanceof Error) throw value;
    if (value?.httpStatus) return reply(value.body || {message: 'Synthetic rejected'}, value.httpStatus);
    if (value === undefined) value = method === 'GET' ? [] : {id: 'created'};
    return reply(Array.isArray(value) ? {results: value, count: value.length, next: null} : value);
  });
  return routes;
}
export function reply(body, status = 200) {
  return {ok: status < 400, status, json: async () => body};
}
export function portal(component) { return render(<AppShell>{component}</AppShell>); }
export function change(label, value, root = screen) {
  fireEvent.change(root.getByLabelText(label), {target: {value}});
}
export function submit(label, root = screen) {
  const button = root.getByRole('button', {name: label});
  fireEvent.submit(button.closest('form'));
}
export function writes(url) {
  return fetch.mock.calls.filter(([u, o]) => u === url && o?.method && o.method !== 'GET');
}
