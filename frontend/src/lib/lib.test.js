import { all, api, ApiError } from "./api";
import { dateTime, money } from "./format";
import { navGroup, roleLabel } from "./roles";

const response = (body, status = 200) => ({
  ok: status < 400,
  status,
  json: async () => body,
});

test("role labels and navigation groups cover each menu category", () => {
  expect(roleLabel("DIRECTOR")).toBe("Admin");
  expect(roleLabel("CHIEF_WARDEN")).toBe("Chief Warden");
  expect(roleLabel()).toBe("");
  expect(navGroup("/dashboard")).toBe("Overview");
  expect(navGroup("/profile")).toBe("People & account");
  expect(navGroup("/leave/review")).toBe("Requests & records");
  expect(navGroup("/director")).toBe("Administration");
  expect(navGroup("/laundry")).toBe("Hostel services");
});

test("format helpers return safe placeholders and localized values", () => {
  expect(dateTime()).toBe("—");
  expect(dateTime("2026-01-01T00:00:00Z")).toContain("2026");
  expect(money("25")).toContain("25");
});

test("api validates paths, attaches csrf for writes, and surfaces server errors", async () => {
  await expect(api("/not-api/")).rejects.toThrow("Same-origin");
  global.fetch = jest
    .fn()
    .mockResolvedValueOnce(response({ csrfToken: "token" }))
    .mockResolvedValueOnce(response({ saved: true }, 201));
  await expect(api("/api/profile/", { method: "PATCH", body: { phone: "1" } })).resolves.toEqual({ saved: true });
  expect(global.fetch.mock.calls[1][1]).toMatchObject({
    method: "PATCH",
    headers: expect.objectContaining({ "X-CSRFToken": "token" }),
  });

  global.fetch = jest.fn().mockResolvedValue(response({ message: "No access" }, 403));
  await expect(api("/api/profile/")).rejects.toEqual(expect.objectContaining({ status: 403, message: "No access" }));

  global.fetch = jest.fn().mockResolvedValue(response({ message: "Missing CSRF" }, 403));
  await expect(api("/api/profile/", { method: "POST" })).rejects.toBeInstanceOf(ApiError);
});

test("all follows paginated API results and returns non-list API payloads", async () => {
  global.fetch = jest.fn((path) => {
    if (path === "/api/items/") return Promise.resolve(response({ results: [{ id: 1 }], next: "http://localhost/api/items/?page=2" }));
    if (path === "/api/items/?page=2") return Promise.resolve(response({ results: [{ id: 2 }], next: null }));
    return Promise.resolve(response({ status: "ok" }));
  });
  await expect(all("/api/items/")).resolves.toEqual([{ id: 1 }, { id: 2 }]);
  await expect(all("/api/health/")).resolves.toEqual({ status: "ok" });
});
