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

import ProfilePanel from "./ProfilePanel";
test("profile protects identity and saves only the phone field", async () => {
  global.fetch = jest.fn(async (url) =>
    url === "/api/auth/csrf/"
      ? response({ csrfToken: "test" })
      : response({
          name: "Arin",
          username: "student",
          role: "STUDENT",
          profile: {
            srn: "DEMO-1",
            room: "204",
            hostel: "Block A",
            phone: "9000099999",
          },
        }),
  );
  render(<ProfilePanel />);
  expect(screen.getByText("DEMO-1")).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("Phone number"), {
    target: { value: "9000099999" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Save" }));
  await screen.findByText("Contact details saved.");
  expect(
    JSON.parse(fetch.mock.calls.find(([, o]) => o?.method === "PATCH")[1].body),
  ).toEqual({ phone: "9000099999" });
});
