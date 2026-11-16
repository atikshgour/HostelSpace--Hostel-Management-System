/* Team test review | US-01/18/21 | frontend validation and visible request states. */
import {act, fireEvent, render, screen, waitFor} from "@testing-library/react";
import LoginForm from "./LoginForm";

const mockReplace = jest.fn();
jest.mock("next/navigation", () => ({
  useRouter: () => ({replace: mockReplace, refresh: jest.fn()}),
}));
const response = (body, status=200) => ({ok:status<400, status, json:async()=>body});
beforeEach(() => {
  mockReplace.mockClear();
  global.fetch = jest.fn();
});
function fill() {
  fireEvent.change(screen.getByLabelText("Username"), {target:{value:"synthetic-student"}});
  fireEvent.change(screen.getByLabelText("Password"), {target:{value:"synthetic-test-value"}});
}

test("frontend: incomplete login stays invalid and does not send a request", () => {
  render(<LoginForm />);
  expect(screen.getByLabelText("Username")).toBeInvalid();
  expect(screen.getByLabelText("Password")).toBeInvalid();
  fireEvent.click(screen.getByRole("button", {name:"Sign in"}));
  expect(fetch).not.toHaveBeenCalled();
});

test("frontend: pending sign-in disables repeat submission, then navigates on success", async () => {
  let complete;
  global.fetch = jest.fn(url => url === "/api/auth/csrf/"
    ? Promise.resolve(response({csrfToken:"synthetic-csrf"}))
    : new Promise(resolve => {complete=resolve;}));
  render(<LoginForm />);
  fill();
  fireEvent.click(screen.getByRole("button", {name:"Sign in"}));
  expect(await screen.findByRole("button", {name:/Signing in/})).toBeDisabled();
  await waitFor(() => expect(complete).toEqual(expect.any(Function)));
  await act(async () => complete(response({role:"STUDENT"})));
  await waitFor(() => expect(mockReplace).toHaveBeenCalledWith("/dashboard"));
  expect(screen.getByRole("button", {name:"Sign in"})).toBeEnabled();
});

test("frontend: transport failure is visible and permits a later retry", async () => {
  global.fetch = jest.fn(async () => {throw new Error("Synthetic connection unavailable");});
  render(<LoginForm />);
  fill();
  fireEvent.click(screen.getByRole("button", {name:"Sign in"}));
  expect(await screen.findByRole("alert")).toHaveTextContent("Synthetic connection unavailable");
  expect(screen.getByRole("button", {name:"Sign in"})).toBeEnabled();
  expect(mockReplace).not.toHaveBeenCalled();
});
