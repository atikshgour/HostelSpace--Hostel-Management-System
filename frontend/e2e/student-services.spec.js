const { test, expect } = require("@playwright/test");
const fs = require("fs"),
  path = require("path");
const password = process.env.HOSTELSPACE_DEMO_PASSWORD;
if (!password)
  throw new Error(
    "Set HOSTELSPACE_DEMO_PASSWORD privately to the seeded account password.",
  );
async function login(page, user) {
  await page.goto("/login");
  await page.getByLabel("Username", { exact: true }).fill(user);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page).toHaveURL(/dashboard/);
  await expect(
    page.getByRole("heading", { name: "HostelSpace", exact: true }),
  ).toBeVisible();
}
async function api(page, url, method = "GET", body) {
  let headers = {};
  if (method !== "GET") {
    const c = await page.request.get("/api/auth/csrf/");
    headers["X-CSRFToken"] = (await c.json()).csrfToken;
  }
  const r = await page.request.fetch(url, {
    method,
    headers,
    ...(body ? { data: body } : {}),
  });
  expect(r.ok(), `${method} ${url}: ${await r.text()}`).toBeTruthy();
  return r.json();
}
async function rejected(page, url, body, status) {
  const c = await page.request.get("/api/auth/csrf/");
  const r = await page.request.post(url, {
    headers: { "X-CSRFToken": (await c.json()).csrfToken },
    data: body,
  });
  expect(r.status()).toBe(status);
}
async function screenshot(page, name) {
  const dir = path.resolve(__dirname, "../test-results/evidence");
  fs.mkdirSync(dir, { recursive: true });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: path.join(dir, name + ".png"),
    fullPage: false,
    animations: "disabled",
  });
}

test("TC-FR07-01: assigned complaint progresses with retained history", async ({
  page,
}) => {
  const description = "E2E repair " + Date.now();
  await login(page, "student");
  await page.goto("/complaints");
  await page.getByRole("button", { name: "+ New complaint" }).click();
  let dialog = page.getByRole("dialog");
  await dialog
    .getByRole("combobox", { name: "Category", exact: true })
    .selectOption("Plumbing");
  await dialog.getByLabel("Description").fill(description);
  await dialog.getByRole("button", { name: "Submit complaint" }).click();
  await expect(
    page.getByRole("row").filter({ hasText: description }),
  ).toBeVisible();
  await login(page, "director");
  await page.goto("/complaints/manage");
  await page
    .getByRole("row")
    .filter({ hasText: description })
    .getByRole("link", { name: "Open complaint" })
    .click();
  await page
    .getByRole("combobox", { name: "Maintenance staff", exact: true })
    .selectOption({ label: "maintenance" });
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect(page.getByRole("status")).toContainText("Changes saved.");
  await login(page, "maintenance");
  await page.goto("/complaints/manage");
  await page
    .getByRole("row")
    .filter({ hasText: description })
    .getByRole("link", { name: "Open complaint" })
    .click();
  for (const state of ["In Progress", "Resolved"]) {
    await page
      .getByRole("combobox", { name: "Next status", exact: true })
      .selectOption(state);
    await page
      .getByLabel("Progress remarks")
      .fill(state === "Resolved" ? "Repair completed." : "Repair started.");
    await page.getByRole("button", { name: "Save", exact: true }).click();
    await expect(
      page.locator(".hs-badge").getByText(state, { exact: true }),
    ).toBeVisible();
  }
  await screenshot(page, "complaint-resolved");
});
test('TC-FR08-01: Mess Staff allocates, students read only their own current records', async ({page}) => {
  const name='Synthetic hall '+Date.now();
  const code='COUPON-'+Date.now();
  await login(page,'mess');
  await page.goto('/mess/manage');
  await page.getByRole('button',{name:'+ Add mess option'}).click();
  let dialog=page.getByRole('dialog');
  await dialog.getByLabel('Mess name',{exact:true}).fill(name);
  await dialog.getByRole('combobox',{name:'Meal type',exact:true}).selectOption('Vegetarian');
  await dialog.getByLabel('Capacity',{exact:true}).fill('10');
  await dialog.getByRole('button',{name:'Save changes'}).click();
  await expect(page.getByRole('dialog')).toHaveCount(0);
  await expect(page.getByRole('heading',{name,exact:true})).toBeVisible();
  await page.getByRole('button',{name:'Select for student'}).click();
  dialog=page.getByRole('dialog');
  await dialog.getByRole('combobox',{name:'Student',exact:true}).selectOption({label:'student'});
  const option=(await api(page,'/api/mess/options/')).results.find(x=>x.name===name);
  await dialog.getByRole('combobox',{name:'Mess option',exact:true}).selectOption(String(option.id));
  await dialog.getByRole('button',{name:'Save changes'}).click();
  await expect(page.getByRole('dialog')).toHaveCount(0);
  await expect(page.getByRole('status')).toContainText('Mess details updated.');
  await page.getByRole('button',{name:'+ Issue coupon'}).click();
  dialog=page.getByRole('dialog');
  await dialog.getByRole('combobox',{name:'Student',exact:true}).selectOption({label:'student'});
  await dialog.getByLabel('Coupon code',{exact:true}).fill(code);
  await dialog.getByLabel('Valid from',{exact:true}).fill('2026-01-01');
  await dialog.getByLabel('Valid until',{exact:true}).fill('2099-12-31');
  await dialog.getByRole('button',{name:'Save changes'}).click();
  await expect(page.getByRole('dialog')).toHaveCount(0);
  await expect(page.getByRole('status')).toContainText('Mess details updated.');
  await login(page,'student');
  await page.goto('/mess');
  await expect(page.getByRole('heading',{name,exact:true}).first()).toBeVisible();
  await expect(page.getByText(code,{exact:true})).toBeVisible();
  await expect(page.getByRole('button',{name:'Choose this mess'})).toHaveCount(0);
  const me=await api(page,'/api/auth/me/');
  await rejected(page,'/api/mess/select/',{student:me.id,option:option.id},403);
  await login(page,'student2');
  const coupons=await api(page,'/api/mess/coupons/');
  expect(coupons.results.some(x=>x.code===code)).toBeFalsy();
});

test('TC-FR09-01: simulated payment persists Paid and a retained attempt', async ({page}) => {
  await login(page, 'director');
  const students=await api(page, '/api/choices/users/?role=STUDENT');
  const feeTitle='Browser fee '+Date.now();
  await api(page, '/api/fees/', 'POST', {student:students.results[0].id,
    title:feeTitle, amount:'10.00', currency:'INR', due_date:'2026-12-31'});
  await login(page, 'student');
  await page.goto('/fees');
  const feeCard=page.locator('.hs-card').filter({has:page.getByRole('heading',{name:feeTitle,exact:true})});
  await feeCard.getByRole('button', {name:'Open test checkout'}).click();
  await expect(page.getByRole('dialog', {name:'Local payment simulation'})).toBeVisible();
  await page.getByRole('button', {name:'Simulate success',exact:true}).click();
  await expect(page.getByRole('status')).toContainText('No real payment was made.');
  await page.reload();
  await expect(feeCard.getByText('Paid',{exact:true})).toBeVisible();
  const attempts=await api(page, '/api/payments/attempts/');
  expect(attempts.results.some(x=>x.status==='Success')).toBeTruthy();
});
