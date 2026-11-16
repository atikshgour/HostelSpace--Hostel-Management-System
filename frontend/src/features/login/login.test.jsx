/* Owner: Anvi Srinivas | US-01 | Dev sprint 1 | SRS sprint 1 | Reviewer: Arin Singh (pending) */
import { render, screen, fireEvent } from "@testing-library/react";
import LoginForm from "./LoginForm";
const mockReplace = jest.fn();
jest.mock("next/navigation", () => ({
  useRouter: () => ({ replace: mockReplace, refresh: jest.fn() }),
}));
const response = (body, status = 200) => ({
  ok: status < 400,
  status,
  json: async () => body,
});
beforeEach(() => {
  global.fetch = jest.fn(async (url) =>
    url === "/api/auth/csrf/"
      ? response({ csrfToken: "test" })
      : response({ role: "STUDENT" }),
  );
});
test("login sends session credentials through CSRF transport", async () => {
  render(<LoginForm />);
  fireEvent.change(screen.getByLabelText("Username"), {
    target: { value: "student" },
  });
  fireEvent.change(screen.getByLabelText("Password"), {
    target: { value: "unit-only" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Sign in" }));
  await screen.findByRole("button", { name: "Sign in" });
  expect(
    await new Promise((r) =>
      setTimeout(() => r(mockReplace.mock.calls.length), 20),
    ),
  ).toBeGreaterThan(0);
  const call = fetch.mock.calls.find(([url]) => url === "/api/auth/login/");
  expect(call[1].headers["X-CSRFToken"]).toBe("test");
  expect(localStorage.length).toBe(0);
});
test("invalid login displays backend error", async () => {
  global.fetch = jest.fn(async (url) =>
    url === "/api/auth/csrf/"
      ? response({ csrfToken: "test" })
      : response({ message: "Invalid username or password." }, 400),
  );
  render(<LoginForm />);
  fireEvent.change(screen.getByLabelText("Username"), {
    target: { value: "student" },
  });
  fireEvent.change(screen.getByLabelText("Password"), {
    target: { value: "wrong" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Sign in" }));
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Invalid username or password.",
  );
});

test("sign-in fallback never submits credentials in a URL", () => {
  render(<LoginForm />);
  expect(screen.getByLabelText("Password").closest("form")).toHaveAttribute(
    "method",
    "post",
  );
});
