/* Owner: Atiksh Gour | US-13,US-14 | Dev sprint 2 | SRS sprint 4 | Reviewer: Anvi Srinivas (pending) */
import { render, screen, fireEvent } from "@testing-library/react";
const response = (body, status = 200) => ({
  ok: status < 400,
  status,
  json: async () => body,
});
jest.mock("@/components/ui/AppShell", () => ({
  ...jest.requireActual("@/components/ui/AppShell"),
  useIdentity: () => ({
    id: 1,
    name: "Arin",
    username: "student",
    role: "STUDENT",
    profile: {
      srn: "DEMO-1",
      room: "204",
      hostel: "Block A",
      phone: "9000012345",
    },
  }),
}));

import ComplaintList from "./ComplaintList";
test("student submits category and description, never room or identity", async () => {
  global.fetch = jest.fn(async (url, o = {}) =>
    url === "/api/auth/csrf/"
      ? response({ csrfToken: "test" })
      : o.method === "POST"
        ? response({ id: 1 }, 201)
        : response({ results: [] }),
  );
  render(<ComplaintList />);
  fireEvent.click(await screen.findByRole("button", { name: /New complaint/ }));
  fireEvent.change(screen.getByLabelText("Category"), {
    target: { value: "Plumbing" },
  });
  fireEvent.change(screen.getByLabelText("Description"), {
    target: { value: "Leaking tap" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Submit complaint" }));
  await screen.findByText(
    "Complaint submitted. The Director can assign it for repair.",
  );
  expect(
    JSON.parse(fetch.mock.calls.find(([, o]) => o?.method === "POST")[1].body),
  ).toEqual({ category: "Plumbing", description: "Leaking tap" });
});
