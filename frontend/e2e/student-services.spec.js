const { test, expect } = require("@playwright/test");
const fs = require("fs"),
  path = require("path");
const password = process.env.HOSTELSPACE_DEMO_PASSWORD;
if (!password)
  throw new Error(
    "Set HOSTELSPACE_DEMO_PASSWORD privately to the seeded account password.",
  );
// Keep test sessions in worker memory; never write credentials/cookies to artifacts.
const sessions = new Map();
async function login(page, user) {
  await page.context().clearCookies();
  if (sessions.has(user)) {
    await page.context().addCookies(sessions.get(user));
    const me = await page.request.get('/api/auth/me/');
    if (me.ok()) {
      await page.goto('/dashboard');
      await expect(page.getByRole('heading', {name: /Welcome back,/})).toBeVisible();
      return;
    }
    sessions.delete(user);
    await page.context().clearCookies();
  }
  await page.goto("/login");
  await page.getByLabel("Username", { exact: true }).fill(user);
  await page.getByLabel("Password", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page).toHaveURL(/dashboard/);
  await expect(
    page.getByRole("heading", { name: /Welcome back,/ }),
  ).toBeVisible();
  sessions.set(user, await page.context().cookies());
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
  await dialog.getByRole('combobox',{name:'Student',exact:true}).selectOption({label:'Arin V.'});
  const option=(await api(page,'/api/mess/options/')).results.find(x=>x.name===name);
  await dialog.getByRole('combobox',{name:'Mess option',exact:true}).selectOption(String(option.id));
  await dialog.getByRole('button',{name:'Save changes'}).click();
  await expect(page.getByRole('dialog')).toHaveCount(0);
  await expect(page.getByRole('status')).toContainText('Mess details updated.');
  await page.getByRole('button',{name:'+ Issue coupon'}).click();
  dialog=page.getByRole('dialog');
  await dialog.getByRole('combobox',{name:'Student',exact:true}).selectOption({label:'Arin V.'});
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
  await page.goto('/director');
  await expect(page.getByRole('heading',{name:'Director overview',exact:true})).toBeVisible();
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

test("session, profile persistence and accessible mobile navigation", async ({
  page,
}) => {
  await login(page, "student");
  await expect(page.getByText("Get things done")).toBeVisible();
  await screenshot(page, "student-dashboard");
  await page.goto("/profile");
  await page.getByLabel("Phone number").fill("+919000012345");
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect(page.getByRole("status")).toHaveText("Contact details saved.");
  await page.reload();
  await expect(page.getByLabel("Phone number")).toHaveValue("+919000012345");
  await page.setViewportSize({ width: 390, height: 844 });
  await screenshot(page, "mobile-profile");
  await page.getByRole("button", { name: "Open navigation menu" }).click();
  await expect(
    page.getByRole("link", { name: "Mess & coupons" }),
  ).toBeVisible();
  await screenshot(page, "mobile-navigation");
  await page.keyboard.press("Escape");
  await expect(
    page.getByRole("button", { name: "Open navigation menu" }),
  ).toBeFocused();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  await page.getByRole("button", { name: "Sign out" }).click();
  await expect(page).toHaveURL(/login/);
  expect((await page.request.get("/api/auth/me/")).status()).toBe(403);
});

test("published announcements, rules and study-room status", async ({
  page,
}) => {
  await login(page, "student");
  await page.goto("/information");
  await expect(
    page.getByRole("heading", { name: "Welcome to HostelSpace" }),
  ).toBeVisible();
  await screenshot(page, "announcements");
  await page.getByRole("button", { name: "Rules", exact: true }).click();
  await expect(page.getByText("Return before 8 PM")).toBeVisible();
  await screenshot(page, "hostel-rules");
  await page.goto("/study-room");
  await expect(page.getByText("Open", { exact: true })).toBeVisible();
  await screenshot(page, "study-room");
});

test("TC-FR11-01: Director creates assigned accounts; Warden cannot manage accounts", async ({
  page,
}) => {
  await login(page, "director");
  await page.goto("/director/users");
  const suffix = Date.now();
  await page
    .getByRole("button", { name: "+ Create account", exact: true })
    .click();
  let dialog = page.getByRole("dialog");
  await dialog
    .getByLabel("Username", { exact: true })
    .fill("resident" + suffix);
  await dialog.getByLabel("First name", { exact: true }).fill("New Resident");
  await dialog.getByLabel("Initial password").fill(password);
  await dialog.getByLabel("Student number / SRN").fill("STU" + suffix);
  await dialog.getByLabel("Room number").fill("305");
  await dialog.getByLabel("Hostel block").fill("Block A");
  const wardens = (await api(page, '/api/director/users/')).results;
  await dialog.getByRole('combobox', {name:'Assigned Warden', exact:true})
    .selectOption(String(wardens.find(u=>u.username==='warden').id));
  await screenshot(page, "warden-account-dialog");
  await dialog
    .getByRole("button", { name: "Create account", exact: true })
    .click();
  await expect(dialog).not.toBeVisible();
  await expect(page.getByRole("status")).toContainText("Account created");
  await page.getByLabel("Search people").fill("resident" + suffix);
  await expect(
    page.getByRole("row").filter({ hasText: "resident" + suffix }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "+ Create account", exact: true })
    .click();
  dialog = page.getByRole("dialog");
  await dialog
    .getByRole("combobox", { name: "Account type", exact: true })
    .selectOption("LAUNDRY_STAFF");
  await dialog.getByLabel("Username", { exact: true }).fill("laundry" + suffix);
  await dialog
    .getByLabel("First name", { exact: true })
    .fill("New Laundry Staff");
  await dialog.getByLabel("Initial password").fill(password);
  await dialog
    .getByRole("button", { name: "Create account", exact: true })
    .click();
  await expect(dialog).not.toBeVisible();
  await expect(page.getByRole("status")).toContainText("Account created");
  await page.getByLabel("Search people").fill("");
  await screenshot(page, "warden-people");
  await login(page, 'warden');
  expect((await page.request.get('/api/director/users/')).status()).toBe(403);
  await rejected(page, '/api/director/users/',
    {username:'forbidden'+suffix, role:'DIRECTOR', password}, 403);
});

test("automatic laundry groups, configurable return time, ready and collection", async ({
  page,
}) => {
  await login(page, "laundry");
  await page.goto("/laundry/manage");
  await expect(
    page.getByRole("heading", { name: "Student timetable" }),
  ).toBeVisible();
  await screenshot(page, "laundry-group-schedule");
  await page.getByRole("button", { name: "Change return time" }).click();
  let dialog = page.getByRole("dialog");
  await dialog.getByLabel("Return after (days)").fill("5");
  await dialog.getByRole("button", { name: "Save", exact: true }).click();
  await expect(page.getByText("5 days", { exact: true })).toBeVisible();
  await page.goto("/laundry/handover");
  await page.getByRole("button", { name: "+ Receive clothes" }).click();
  dialog = page.getByRole("dialog");
  await dialog
    .getByRole("combobox", { name: "Student", exact: true })
    .selectOption({ label: "Arin V. · DEMO-001" });
  const items = "E2E scheduled laundry " + Date.now();
  await dialog.getByLabel("Item details").fill(items);
  await dialog.getByLabel("Number of items").fill("4");
  await expect(dialog.getByLabel("Return after (days)")).toHaveValue("5");
  await dialog.getByLabel("Return after (days)").fill("4");
  await screenshot(page, "laundry-receive-dialog");
  await dialog.getByRole("button", { name: "Record handover" }).click();
  let row = page.getByRole("row").filter({ hasText: items });
  await expect(row).toBeVisible();
  const records = (await api(page, "/api/laundry/records/")).results;
  const record = records.find((x) => x.item_details === items);
  expect(record.group_number).toBe(1);
  const before = record.expected_return_date;
  await api(page, "/api/laundry/policy/", "PUT", { turnaround_days: 3 });
  expect(
    (await api(page, "/api/laundry/records/")).results.find(
      (x) => x.id === record.id,
    ).expected_return_date,
  ).toBe(before);
  await row.getByRole("button", { name: "Mark ready" }).click();
  await expect(row.getByText("Ready", { exact: true })).toBeVisible();
  await screenshot(page, "laundry-work-queue");
  page.once("dialog", (d) => d.accept());
  await row.getByRole("button", { name: "Confirm collection" }).click();
  await page
    .getByRole("combobox", { name: "Batch status" })
    .selectOption("Collected");
  await expect(row.getByText("Collected", { exact: true })).toBeVisible();
  await login(page, "student");
  await page.goto("/laundry");
  await expect(page.getByText("Group 1", { exact: true })).toBeVisible();
  await screenshot(page, "student-laundry");
});

test("student leave submission and Warden to Chief escalation", async ({
  page,
}) => {
  const reason = "E2E leave " + Date.now();
  await login(page, "student");
  await page.goto("/leave");
  await page.getByRole("button", { name: "+ Request leave" }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("Start date").fill(new Date(Date.now()+86400000).toISOString().slice(0,10));
  await dialog.getByLabel("End date").fill(new Date(Date.now()+172800000).toISOString().slice(0,10));
  await dialog.getByLabel("Reason", { exact: true }).fill(reason);
  await dialog.getByRole("button", { name: "Submit leave" }).click();
  await expect(page.getByRole("status")).toContainText("Pending status");
  await login(page, "warden");
  await page.goto("/leave/review");
  let row = page.getByRole("row").filter({ hasText: reason });
  await row.getByRole("link", { name: "Open request" }).click();
  await page
    .getByRole("combobox", { name: "Decision", exact: true })
    .selectOption("Escalated");
  await page
    .getByLabel("Decision remarks")
    .fill("Please review extended leave.");
  page.once("dialog", (d) => d.accept());
  await page.getByRole("button", { name: "Save decision" }).click();
  await expect(page.getByText("Escalated", { exact: true })).toBeVisible();
  await login(page, "chief");
  await page.goto("/leave/review");
  row = page.getByRole("row").filter({ hasText: reason });
  await row.getByRole("link", { name: "Open request" }).click();
  await page
    .getByRole("combobox", { name: "Decision", exact: true })
    .selectOption("Approved");
  await page.getByLabel("Decision remarks").fill("Approved after review.");
  page.once("dialog", (d) => d.accept());
  await page.getByRole("button", { name: "Save decision" }).click();
  await expect(page.getByText("Approved", { exact: true })).toBeVisible();
  await screenshot(page, "leave-approved");
});

test("one-time geolocation attendance and deviation snapshot totals", async ({
  page,
  context,
}) => {
  await login(page, "warden");
  const title = "E2E attendance " + Date.now();
  await api(page, "/api/attendance/sessions/", "POST", {
    title,
    opens_at: new Date(Date.now() - 60000).toISOString(),
    closes_at: new Date(Date.now() + 600000).toISOString(),
    centre_latitude: 12,
    centre_longitude: 77,
    radius_m: 100,
    max_accuracy_m: 50,
    max_sample_age_seconds: 60,
  });
  let students = (await api(page, "/api/arin/students/")).results;
  let student = students.find((x) => x.name === "Arin V.");
  let rules = (await api(page, "/api/arin/rules/")).results;
  await page.goto("/deviations/manage");
  await page
    .getByRole("combobox", { name: "Assigned student", exact: true })
    .selectOption(String(student.id));
  await page
    .getByRole("combobox", { name: "Active rule", exact: true })
    .selectOption(String(rules[0].id));
  const remark = "E2E late return " + Date.now();
  await page.getByLabel("Remarks", { exact: true }).fill(remark);
  await page.getByRole("button", { name: "Record deviation" }).click();
  await expect(
    page.locator("article").getByText(remark, { exact: true }),
  ).toBeVisible();
  await screenshot(page, "deviation-management");
  await context.grantPermissions(["geolocation"]);
  await context.setGeolocation({ latitude: 12, longitude: 77, accuracy: 5 });
  await login(page, "student");
  await page.goto("/attendance");
  const card = page.locator("article").filter({ hasText: title });
  await card
    .getByRole("button", { name: "Submit one-time location attendance" })
    .click();
  await expect(card.getByRole("status")).toContainText("Accepted");
  const history = await api(page, "/api/attendance/history/");
  expect(JSON.stringify(history)).not.toContain("latitude");
  await screenshot(page, "attendance-accepted");
});


test("TC-FR02-01: Content Staff publication appears on resident dashboard", async ({
  page,
}) => {
  const title = "Collection counter update " + Date.now();
  await login(page, "content");
  await page.goto("/information/manage");
  await page.getByRole("button", { name: "+ Publish announcement" }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("Title", { exact: true }).fill(title);
  await dialog
    .getByLabel("Content", { exact: true })
    .fill("The laundry counter will remain open until 7 PM today.");
  await screenshot(page, "announcement-editor-dialog");
  await dialog.getByRole("button", { name: "Save", exact: true }).click();
  await expect(page.getByText(title, { exact: true })).toBeVisible();
  await screenshot(page, "warden-announcements");
  await login(page, "student");
  await expect(
    page.getByRole("heading", { name: title, exact: true }),
  ).toBeVisible();
  await page.goto("/information");
  await expect(
    page.getByRole("heading", { name: title, exact: true }),
  ).toBeVisible();
});