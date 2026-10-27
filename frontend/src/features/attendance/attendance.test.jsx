import { fireEvent, render, screen } from "@testing-library/react";
import AttendanceWorkspace from "./AttendanceHistory";

function response(body, status = 200) { return { ok: status < 400, status, json: async () => body }; }
beforeEach(() => {
  global.fetch = jest.fn(async (url, options = {}) => {
    if (url === "/api/auth/me/") return response({ id: "s1", role: "STUDENT" });
    if (url === "/api/auth/csrf/") return response({ csrfToken: "test" });
    if (String(url).startsWith("/api/attendance/sessions/")) return response({ next: null, results: [{ id: "session-1", title: "Evening", opens_at: "2026-09-28T10:00:00Z", closes_at: "2026-09-28T11:00:00Z", radius_m: 50, max_accuracy_m: 30 }] });
    if (String(url).startsWith("/api/attendance/history/")) return response({ next: null, results: [] });
    if (url === "/api/attendance/submit/" && options.method === "POST") return response({ result: "Accepted", reason_code: "WITHIN_POLICY" }, 201);
    return response({}, 404);
  });
  Object.defineProperty(global.navigator, "geolocation", { configurable: true, value: { getCurrentPosition: jest.fn(callback => callback({ coords: { latitude: 12, longitude: 77, accuracy: 5 }, timestamp: Date.now() })) } });
});

test("geolocation is requested only after the explicit submit click", async () => {
  render(<AttendanceWorkspace />);
  const button = await screen.findByRole("button", { name: /one-time location attendance/ });
  expect(navigator.geolocation.getCurrentPosition).not.toHaveBeenCalled();
  fireEvent.click(button);
  expect(navigator.geolocation.getCurrentPosition).toHaveBeenCalledTimes(1);
  expect(await screen.findByText(/Accepted · WITHIN_POLICY/)).toBeInTheDocument();
  const body = JSON.parse(fetch.mock.calls.find(([url]) => url === "/api/attendance/submit/")[1].body);
  expect(body).toMatchObject({ session: "session-1", latitude: 12, longitude: 77, accuracy_m: 5 });
  expect(localStorage.length).toBe(0);
});
