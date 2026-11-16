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

import LaundryPanel from "./LaundryPanel";
test("student sees automatic weekday and cannot change policy or collect batches", async () => {
  global.fetch = jest.fn(async (url) =>
    response({
      results: url.includes("allocations") ? [{ weekday: "Saturday" }] : [],
    }),
  );
  render(<LaundryPanel />);
  expect(await screen.findByText(/Saturday drop-off/)).toBeInTheDocument();
  expect(
    screen.queryByRole("button", { name: /assign|collect/i }),
  ).not.toBeInTheDocument();
});
