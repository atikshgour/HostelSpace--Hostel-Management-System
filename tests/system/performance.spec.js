const { test, expect } = require("@playwright/test");
test("low-volume local health-response smoke check", async ({ request }) => {
  let times = [];
  for (let i = 0; i < 8; i++) {
    let before = Date.now();
    const r = await request.get("/health/");
    expect(r.ok()).toBeTruthy();
    expect((await r.json()).status).toBe("ok");
    times.push(Date.now() - before);
  }
  expect(Math.max(...times)).toBeLessThan(5000);
});
