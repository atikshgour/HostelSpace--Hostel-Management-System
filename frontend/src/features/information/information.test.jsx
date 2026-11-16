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

import InformationTabs from "./InformationTabs";
test("information tabs display real API notices and rules", async () => {
  global.fetch = jest.fn(async (url) =>
    response({
      results:
        url === "/api/rules/"
          ? [
              {
                id: 3,
                title: "Quiet hours",
                body: "Keep noise low",
                weightage: "2.00",
              },
            ]
          : [
              {
                id: 1,
                kind: "notice",
                title: "Water maintenance",
                body: "Please store water",
              },
            ],
    }),
  );
  render(<InformationTabs />);
  expect(await screen.findByText("Water maintenance")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Rules" }));
  expect(await screen.findByText("Quiet hours")).toBeInTheDocument();
  expect(screen.queryByText("Water maintenance")).not.toBeInTheDocument();
});
