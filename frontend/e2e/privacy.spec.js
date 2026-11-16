import { test, expect } from "@playwright/test";

async function mockIdentityAndEmptyApis(page, role) {
  await page.route("**/api/auth/me/", route => route.fulfill({ json: { id: "test-user", name: "Synthetic student", username: "student", role } }));
  await page.route("**/api/leaves/**", route => route.fulfill({ json: { count: 0, next: null, previous: null, results: [] } }));
  await page.route("**/api/attendance/**", route => route.fulfill({ json: { count: 0, next: null, previous: null, results: [] } }));
  await page.route("**/api/deviations/**", route => route.fulfill({ json: route.request().url().includes("total") ? { active_total: "0.00" } : { count: 0, next: null, previous: null, results: [] } }));
}

test("attendance never requests location before the student clicks", async ({ page, context }) => {
  await context.grantPermissions(["geolocation"]);
  await context.setGeolocation({ latitude: 12, longitude: 77, accuracy: 5 });
  await mockIdentityAndEmptyApis(page, "STUDENT");
  await page.addInitScript(() => {
    window.locationRequests = 0;
    const original = navigator.geolocation.getCurrentPosition.bind(navigator.geolocation);
    navigator.geolocation.getCurrentPosition = (...args) => {
      window.locationRequests += 1;
      return original(...args);
    };
  });
  let locationWrites = 0;
  await page.route("**/api/attendance/submit/", route => { locationWrites += 1; return route.fulfill({ json: { result: "Accepted", reason_code: "WITHIN_POLICY" } }); });
  await page.goto("/attendance");
  await expect(page.getByRole("heading", {name: "Attendance", exact: true})).toBeVisible();
  expect(locationWrites).toBe(0);
  expect(await page.evaluate(() => window.locationRequests)).toBe(0);
  expect(await page.evaluate(() => localStorage.length)).toBe(0);
});

test("student deviation view has no write controls", async ({ page }) => {
  await mockIdentityAndEmptyApis(page, "STUDENT");
  await page.goto("/deviations");
  await expect(page.getByRole("heading", {name:"Deviation records", exact:true})).toBeVisible();
  await expect(page.getByRole("button", { name: /Record deviation/i })).toHaveCount(0);
  await expect(page.getByRole("button", { name: /Deactivate/i })).toHaveCount(0);
});
