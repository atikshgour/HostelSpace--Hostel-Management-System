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

import StudyRoomCard from "./StudyRoomCard";
test("study room is read-only and shows the current server status", async () => {
  global.fetch = jest.fn(async () =>
    response({
      status: "Open",
      timings: "6 AM – 10 PM",
      message: "Quiet study",
    }),
  );
  render(<StudyRoomCard />);
  expect(await screen.findByText("Open")).toBeInTheDocument();
  expect(
    screen.queryByRole("button", { name: /book|reserve/i }),
  ).not.toBeInTheDocument();
});
