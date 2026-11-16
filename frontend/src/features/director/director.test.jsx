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

import DirectorPanel from "./DirectorPanel";
test("director report displays zero counts without inventing records", async () => {
  global.fetch = jest.fn(async () =>
    response({
      pending_leave: 0,
      escalated_leave: 0,
      open_complaints: 0,
      unpaid_fees: 0,
      active_students: 0,
      attendance_by_session: [],
    }),
  );
  render(<DirectorPanel />);
  expect(
    await screen.findByText("No attendance sessions."),
  ).toBeInTheDocument();
  expect(screen.getAllByText("0")).toHaveLength(5);
});
