import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import LeaveWorkspace from "./LeaveList";

beforeEach(() => {
  global.fetch = jest.fn(async (url, options = {}) => {
    if (url === "/api/auth/me/") return response({ id: "s1", role: "STUDENT" });
    if (url === "/api/auth/csrf/") return response({ csrfToken: "test" });
    if (url === "/api/leaves/" && options.method === "POST") return response({ id: "l1", status: "Pending" }, 201);
    if (String(url).startsWith("/api/leaves/")) return response({ count: 0, next: null, previous: null, results: [] });
    return response({}, 404);
  });
});
function response(body, status = 200) { return { ok: status < 400, status, json: async () => body }; }

test("student submits validated leave without caller-owned identity fields", async () => {
  render(<LeaveWorkspace />);
  await screen.findByRole("heading", { name: "Apply for leave" });
  fireEvent.change(screen.getByLabelText("Start date"), { target: { value: "2026-09-21" } });
  fireEvent.change(screen.getByLabelText("End date"), { target: { value: "2026-09-22" } });
  fireEvent.change(screen.getByLabelText("Reason"), { target: { value: "Family visit" } });
  fireEvent.click(screen.getByRole("button", { name: "Submit leave" }));
  await screen.findByText(/Pending status/);
  const write = fetch.mock.calls.find(([, options]) => options?.method === "POST");
  expect(JSON.parse(write[1].body)).toEqual({ start_date: "2026-09-21", end_date: "2026-09-22", reason: "Family visit" });
});

test("client rejects reversed dates before an API write", async () => {
  render(<LeaveWorkspace />);
  await screen.findByRole("heading", { name: "Apply for leave" });
  fireEvent.change(screen.getByLabelText("Start date"), { target: { value: "2026-09-22" } });
  fireEvent.change(screen.getByLabelText("End date"), { target: { value: "2026-09-21" } });
  fireEvent.change(screen.getByLabelText("Reason"), { target: { value: "Visit" } });
  fireEvent.click(screen.getByRole("button", { name: "Submit leave" }));
  expect(await screen.findByRole("alert")).toHaveTextContent(/on or after/);
  await waitFor(() => expect(fetch.mock.calls.filter(([, options]) => options?.method === "POST")).toHaveLength(0));
});
