// Owner: Atiksh Gour | US-15 / TC-FR08-01 | Sprint 5 | Reviewer: Anvi Srinivas
// Synthetic sessions arrive on stdin; no persisted traces/cookie storage files.
import { chromium, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';

const { origin, sessions, student } = JSON.parse(readFileSync(0, 'utf8'));
const browser = await chromium.launch({ channel: 'chrome', headless: true });
let debugPage;
async function contextFor(role, mobile = false) {
  const context = await browser.newContext(mobile ? { viewport: { width: 390, height: 844 } } : {});
  await context.addCookies([{ name: 'sessionid', value: sessions[role], url: origin, httpOnly: true, sameSite: 'Lax' }]);
  return context;
}
try {
  const staff = await contextFor('staff');
  const page = await staff.newPage();
  debugPage = page;
  await page.goto(`${origin}/mess/manage`);
  const allocation = page.getByRole('form', { name: 'Create allocation', exact: true });
  await allocation.getByLabel('Student', { exact: true }).selectOption(String(student));
  await allocation.getByLabel('Mess name').fill('Synthetic browser mess');
  await allocation.getByLabel('Valid from').fill('2026-10-29');
  await allocation.getByLabel('Valid until').fill('2026-10-29');
  await allocation.getByRole('button', { name: 'Save allocation' }).click();
  await expect(page.getByRole('form', { name: /Edit allocation/ })).toBeVisible();
  const response = await staff.request.get(`${origin}/api/mess/allocations/`);
  expect(response.status()).toBe(200);
  const record = (await response.json()).results[0];

  async function createCoupon(code, from, until, active = true) {
    const form = page.getByRole('form', { name: 'Create coupon', exact: true });
    await form.getByLabel('Allocation', { exact: true }).selectOption(String(record.id));
    await form.getByLabel('Coupon code').fill(code);
    await form.getByLabel('Valid from').fill(from);
    await form.getByLabel('Valid until').fill(until);
    await form.getByLabel('Active', { exact: true }).setChecked(active);
    await form.getByRole('button', { name: 'Save coupon' }).click();
    await expect(form.getByLabel('Coupon code')).toHaveValue('');
  }
  await createCoupon('SYNTHETIC-VALID', '2026-10-29', '2026-10-29');
  await createCoupon('SYNTHETIC-EXPIRED', '2026-10-27', '2026-10-28');
  await createCoupon('SYNTHETIC-FUTURE', '2026-10-30', '2026-10-31');
  await createCoupon('SYNTHETIC-INACTIVE', '2026-10-29', '2026-10-29', false);
  await page.reload();
  await expect(page.getByRole('form', { name: /Edit coupon/ })).toHaveCount(4);

  const own = await contextFor('student', true);
  const mine = await own.newPage();
  await mine.goto(`${origin}/mess`);
  await expect(mine.getByText('Synthetic browser mess', { exact: true })).toBeVisible();
  await expect(mine.getByText('SYNTHETIC-VALID', { exact: true })).toBeVisible();
  for (const code of ['SYNTHETIC-EXPIRED', 'SYNTHETIC-FUTURE', 'SYNTHETIC-INACTIVE']) {
    await expect(mine.getByText(code, { exact: true })).toHaveCount(0);
  }
  await expect(mine.getByRole('button', { name: /order|redeem/i })).toHaveCount(0);
  expect(await mine.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await mine.reload();
  await expect(mine.getByText('SYNTHETIC-VALID', { exact: true })).toBeVisible();
  const foreign = await contextFor('other');
  const other = await foreign.newPage();
  await other.goto(`${origin}/mess`);
  await expect(other.getByText('No current active mess allocation.')).toBeVisible();
  await expect(other.getByText('No currently valid coupons.')).toBeVisible();

  const edit = page.getByRole('form', { name: `Edit allocation ${record.id}`, exact: true });
  await edit.getByLabel('Active', { exact: true }).uncheck();
  await edit.getByRole('button', { name: 'Save allocation' }).click();
  await expect(page.getByRole('form', { name: `Edit allocation ${record.id}`, exact: true }).getByText(/Version 2/)).toBeVisible();
  await mine.reload();
  await expect(mine.getByText('No current active mess allocation.')).toBeVisible();
  await expect(mine.getByText('No currently valid coupons.')).toBeVisible();
  await mine.goto(`${origin}/mess/manage`);
  await expect(mine.getByRole('alert')).toBeVisible();
  await expect(mine.getByRole('form')).toHaveCount(0);
  console.log('US-15 browser workflow passed');
} catch (error) {
  if (debugPage) console.error(await debugPage.locator('main').innerText());
  throw error;
} finally {
  await browser.close();
}
