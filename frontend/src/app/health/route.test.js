/** @jest-environment node */
// Owner: Atiksh | US-20 / TC-CICD-01 | Sprint 1
import { dynamic, GET } from './route';

test('health returns uncached JSON', async () => {
  expect(dynamic).toBe('force-dynamic');
  const response = GET();
  expect(response.status).toBe(200);
  expect(await response.json()).toEqual({ status: 'ok' });
  expect(response.headers.get('Cache-Control')).toBe('no-store');
});
