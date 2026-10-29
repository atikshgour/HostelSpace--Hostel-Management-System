// Owner: Atiksh Gour | US-14 / TC-FR07-01 | Sprint 4 | Reviewer: Anvi Srinivas
// Credentials arrive only on stdin; no trace/storageState/cookies are persisted.
import { chromium, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

const { origin, sessions, complaint, staff } = JSON.parse(readFileSync(0, 'utf8'));
const browser = await chromium.launch({ channel: 'chrome', headless: true });
let debugPage;
async function contextFor(role) {
  const context = await browser.newContext();
  await context.addCookies([{ name: 'sessionid', value: sessions[role], url: origin, httpOnly: true, sameSite: 'Lax' }]);
  return context;
}
try {
  const director = await contextFor('director');
  const page = await director.newPage();
  debugPage = page;
  page.on('requestfailed', (request) => console.error('Request failed:', request.url(), request.failure()?.errorText));
  page.on('console', (message) => { if (message.type() === 'error') console.error(message.text()); });
  await page.goto(`${origin}/complaints/manage`);
  await expect(page.getByRole('article')).toBeVisible();
  await expect(page.getByRole('heading', { name: `Complaint #${complaint} — Open` })).toBeVisible();
  await page.getByLabel('Maintenance Staff').selectOption(String(staff));
  await page.getByLabel(/Remarks/).fill('Synthetic browser assignment');
  await page.getByRole('button', { name: 'Assign staff' }).click();
  await expect(page.getByRole('status')).toHaveText('Complaint updated.');
  await page.reload();
  await expect(page.getByText(`Assigned staff: #${staff}`)).toBeVisible();

  const maintenance = await contextFor('staff');
  const work = await maintenance.newPage();
  await work.goto(`${origin}/complaints/manage`);
  await expect(work.getByLabel('Maintenance Staff')).toHaveCount(0);
  await work.getByLabel(/Remarks/).fill('Synthetic browser work started');
  await work.getByRole('button', { name: 'Mark In Progress' }).click();
  await expect(work.getByRole('heading', { name: `Complaint #${complaint} — In Progress` })).toBeVisible();
  await work.getByLabel(/Remarks/).fill('Synthetic browser repair complete');
  await work.getByRole('button', { name: 'Mark Resolved' }).click();
  await expect(work.getByRole('heading', { name: `Complaint #${complaint} — Resolved` })).toBeVisible();
  await work.reload();
  await expect(work.getByText('History (4)')).toBeVisible();
  await expect(work.getByLabel(/Remarks/)).toHaveCount(0);

  const other = await contextFor('other');
  const otherPage = await other.newPage();
  await otherPage.goto(`${origin}/complaints/manage`);
  await expect(otherPage.getByText('No complaints available.')).toBeVisible();

  const student = await contextFor('student');
  const response = await student.request.get(`${origin}/api/complaints/${complaint}/`);
  expect(response.status()).toBe(200);
  const persisted = await response.json();
  expect(persisted.status).toBe('Resolved');
  expect(persisted.history).toHaveLength(4);
  expect(persisted.history.at(-1).remarks).toBe('Synthetic browser repair complete');
  const denied = await student.request.get(`${origin}/api/complaints/manage/`);
  expect(denied.status()).toBe(403);
  console.log('US-14 browser workflow passed');
} catch (error) {
  // Only synthetic rendered content, never request headers or session cookies.
  if (debugPage) console.error(await debugPage.locator('main').innerText());
  throw error;
} finally {
  await browser.close();
}
