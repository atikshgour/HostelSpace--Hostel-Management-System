import * as attendance from "./attendance/api";
import * as deviations from "./deviations/api";
import * as leave from "./leave/api";

const response = (body, status = 200) => ({
  ok: status < 400,
  status,
  json: async () => body,
});

for (const [name, client] of Object.entries({ attendance, deviations, leave })) {
  describe(`${name} API client`, () => {
    test("rejects unsafe paths and sends GET and POST requests securely", async () => {
      await expect(client.request("https://outside.test/")).rejects.toThrow("same-origin");
      global.fetch = jest.fn().mockResolvedValue(response({ ok: true }));
      await expect(client.request("/api/example/")).resolves.toEqual({ ok: true });

      global.fetch = jest
        .fn()
        .mockResolvedValueOnce(response({ csrfToken: "csrf" }))
        .mockResolvedValueOnce(response({ saved: true }, 201));
      await expect(client.request("/api/example/", { method: "POST", body: { id: 1 } })).resolves.toEqual({ saved: true });
      expect(global.fetch.mock.calls[1][1]).toMatchObject({
        method: "POST",
        headers: expect.objectContaining({ "X-CSRFToken": "csrf" }),
      });
    });

    test("reports csrf and response failures", async () => {
      global.fetch = jest.fn().mockResolvedValue(response({}, 403));
      await expect(client.request("/api/example/", { method: "POST" })).rejects.toBeInstanceOf(client.ApiError);
      global.fetch = jest.fn().mockResolvedValue(response({ message: "No access" }, 403));
      await expect(client.request("/api/example/")).rejects.toEqual(expect.objectContaining({ status: 403 }));
    });
  });
}

test("attendance helpers use the expected API endpoints", async () => {
  global.fetch = jest.fn().mockResolvedValue(response({}));
  await attendance.getIdentity();
  await attendance.listSessions(2);
  await attendance.listAttendance(3);
  expect(global.fetch.mock.calls.map(([path]) => path)).toEqual([
    "/api/auth/me/", "/api/attendance/sessions/?page=2", "/api/attendance/history/?page=3",
  ]);
});

test("leave and deviation helpers build encoded scoped endpoints", async () => {
  global.fetch = jest.fn().mockResolvedValue(response({}));
  await leave.getLeave("a/b");
  await deviations.listDeviations("student/a", 2);
  await deviations.getTotal("student/a", true);
  await deviations.getTotal("student/a", false);
  expect(global.fetch.mock.calls.map(([path]) => path)).toEqual([
    "/api/leaves/a%2Fb/",
    "/api/deviations/?page=2&student=student%2Fa",
    "/api/deviations/total/?student=student%2Fa",
    "/api/deviations/total/",
  ]);
});
