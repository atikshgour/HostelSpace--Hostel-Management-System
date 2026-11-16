/* Owner: Atiksh Gour | US-15 | Dev sprint 3 | SRS sprint 5 | Reviewer: Anvi Srinivas (pending) */
import { render, screen } from "@testing-library/react";
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

import MessPanel from "./MessPanel";
test("TC-FR08-01: student reads assigned mess and coupons without write controls", async () => {
  global.fetch = jest.fn(async (url) =>
    response({
      results: url.includes("coupons")
        ? [
            {
              id: 1,
              code: "DEMO-COUPON",
              active: true,
              valid_from: "2026-10-01",
              valid_to: "2026-10-31",
            },
          ]
        : url.includes("options")
          ? [
              {
                id: 2,
                name: "Vegetarian hall",
                diet: "Vegetarian",
                available: 10,
                capacity: 20,
                active: true,
              },
            ]
          : url.includes("history")
            ? []
            : [{ id: 1, mess_name: "Main mess" }],
    }),
  );
  render(<MessPanel />);
  expect(await screen.findByText("Main mess")).toBeInTheDocument();
  expect(await screen.findByText("DEMO-COUPON")).toBeInTheDocument();
  expect(
    screen.queryByRole("button", { name: "Choose this mess" }),
  ).not.toBeInTheDocument();
  expect(
    screen.queryByRole("button", { name: "Deactivate" }),
  ).not.toBeInTheDocument();
});
