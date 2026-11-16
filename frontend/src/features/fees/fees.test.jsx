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

import FeesPanel from "./FeesPanel";
test("test checkout displays explicit simulation label and takes no payment credentials", async () => {
  global.fetch = jest.fn(async (url, o = {}) =>
    url === "/api/auth/csrf/"
      ? response({ csrfToken: "test" })
      : url.includes("initiate")
        ? response({
            id: "attempt",
            provider: "simulation",
            amount: "100.00",
            currency: "INR",
          })
        : response({
            results:
              url === "/api/fees/"
                ? [
                    {
                      id: 1,
                      title: "Hostel fee",
                      amount: "100.00",
                      currency: "INR",
                      due_date: "2026-10-31",
                      status: "Unpaid",
                    },
                  ]
                : [],
          }),
  );
  render(<FeesPanel />);
  fireEvent.click(
    await screen.findByRole("button", { name: "Open test checkout" }),
  );
  expect(
    await screen.findByRole("dialog", { name: "Local payment simulation" }),
  ).toHaveTextContent("No funds, card details or real payments.");
  expect(screen.queryByLabelText(/card|pin/i)).not.toBeInTheDocument();
});
