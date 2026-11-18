import { render, screen } from "@testing-library/react";
import { redirect } from "next/navigation";

/* Inline Jest mock components deliberately have no production-facing names. */
/* eslint-disable react/display-name */
jest.mock("next/navigation", () => ({ redirect: jest.fn() }));
jest.mock("next/link", () => ({ children, href }) => <a href={href}>{children}</a>);
jest.mock("@/components/ui/AppShell", () => ({ children }) => <div data-testid="shell">{children}</div>);

jest.mock("@/features/login/LoginForm", () => () => <div>login</div>);
jest.mock("@/features/attendance/AttendanceHistory", () => () => <div>attendance</div>);
jest.mock("@/features/complaints/ComplaintList", () => () => <div>complaints</div>);
jest.mock("@/features/deviations/DeviationPanel", () => () => <div>deviations</div>);
jest.mock("@/features/director/DirectorPanel", () => () => <div>director</div>);
jest.mock("@/features/director/SettingsForm", () => () => <div>settings</div>);
jest.mock("@/features/director/UserManagement", () => () => <div>users</div>);
jest.mock("@/features/fees/FeesPanel", () => () => <div>fees</div>);
jest.mock("@/features/information/InformationTabs", () => () => <div>information</div>);
jest.mock("@/features/information/ContentEditor", () => () => <div>content editor</div>);
jest.mock("@/features/laundry/LaundryPanel", () => () => <div>laundry</div>);
jest.mock("@/features/leave/LeaveList", () => () => <div>leave</div>);
jest.mock("@/features/mess/MessPanel", () => () => <div>mess</div>);
jest.mock("@/features/profile/ProfilePanel", () => () => <div>profile</div>);
jest.mock("@/features/study-room/StudyRoomCard", () => () => <div>study room</div>);
jest.mock("@/features/study-room/StudyRoomEditor", () => () => <div>study room editor</div>);

import Home from "./page";
import Login from "./(auth)/login/page";
import RootLayout, { metadata } from "./layout";
import NotFound from "./not-found";
import PortalLayout from "./(portal)/layout";
import Loading from "./(portal)/loading";
import ErrorPage from "./(portal)/error";
import Attendance from "./(portal)/attendance/page";
import AttendanceManage from "./(portal)/attendance/manage/page";
import Complaints from "./(portal)/complaints/page";
import ComplaintsManage from "./(portal)/complaints/manage/page";
import Deviations from "./(portal)/deviations/page";
import DeviationsManage from "./(portal)/deviations/manage/page";
import Director from "./(portal)/director/page";
import DirectorSettings from "./(portal)/director/settings/page";
import DirectorUsers from "./(portal)/director/users/page";
import Fees from "./(portal)/fees/page";
import FeesResult from "./(portal)/fees/result/page";
import Information from "./(portal)/information/page";
import InformationManage from "./(portal)/information/manage/page";
import Laundry from "./(portal)/laundry/page";
import LaundryHandover from "./(portal)/laundry/handover/page";
import LaundryManage from "./(portal)/laundry/manage/page";
import Leave from "./(portal)/leave/page";
import LeaveReview from "./(portal)/leave/review/page";
import Mess from "./(portal)/mess/page";
import MessManage from "./(portal)/mess/manage/page";
import Profile from "./(portal)/profile/page";
import StudyRoom from "./(portal)/study-room/page";
import StudyRoomManage from "./(portal)/study-room/manage/page";

test("route wrappers render their feature screens", () => {
  const routes = [
    [Login, "login"], [Attendance, "attendance"], [AttendanceManage, "attendance"],
    [Complaints, "complaints"], [ComplaintsManage, "complaints"], [Deviations, "deviations"],
    [DeviationsManage, "deviations"], [Director, "director"], [DirectorSettings, "settings"],
    [DirectorUsers, "users"], [Fees, "fees"], [FeesResult, "fees"], [Information, "information"],
    [InformationManage, "content editor"], [Laundry, "laundry"], [LaundryHandover, "laundry"],
    [LaundryManage, "laundry"], [Leave, "leave"], [LeaveReview, "leave"], [Mess, "mess"],
    [MessManage, "mess"], [Profile, "profile"], [StudyRoom, "study room"],
    [StudyRoomManage, "study room editor"],
  ];
  for (const [Route, text] of routes) {
    const { unmount } = render(<Route />);
    expect(screen.getByText(text)).toBeInTheDocument();
    unmount();
  }
});

test("root and portal layouts preserve children and fallback UI works", () => {
  const reset = jest.fn();
  render(<RootLayout><span>root child</span></RootLayout>);
  expect(screen.getByText("root child")).toBeInTheDocument();
  expect(metadata.title).toBe("HostelSpace");
  render(<PortalLayout><span>portal child</span></PortalLayout>);
  expect(screen.getByTestId("shell")).toHaveTextContent("portal child");
  render(<Loading />);
  expect(screen.getByRole("status")).toHaveTextContent("Loading workspace");
  render(<ErrorPage reset={reset} />);
  screen.getByRole("button", { name: "Try again" }).click();
  expect(reset).toHaveBeenCalledTimes(1);
  render(<NotFound />);
  expect(screen.getByRole("link", { name: /return to dashboard/i })).toHaveAttribute("href", "/dashboard");
});

test("home redirects to the dashboard", () => {
  Home();
  expect(redirect).toHaveBeenCalledWith("/dashboard");
});
