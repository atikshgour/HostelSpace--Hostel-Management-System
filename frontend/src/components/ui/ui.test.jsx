/* Owner: Anvi Srinivas | US-17,US-21 | Dev sprint 1; 4–6 | SRS sprint 1; 6 | Reviewer: Arin Singh (pending) */
import { render, screen, fireEvent } from "@testing-library/react";
import Button from "./Button";
import StatusBadge from "./StatusBadge";
import DataTable from "./DataTable";
import FormField from "./FormField";
import EmptyState from "./EmptyState";
import HistoryTimeline from "./HistoryTimeline";
test("shared components expose accessible labels, status and table headers", () => {
  render(
    <>
      <StatusBadge>Approved</StatusBadge>
      <FormField label="Name" name="name" />
      <DataTable headers={["Room"]} rows={[[204]]} />
    </>,
  );
  expect(screen.getByText("Approved")).toHaveClass("Approved");
  expect(screen.getByLabelText("Name")).toBeInTheDocument();
  expect(
    screen.getByRole("columnheader", { name: "Room" }),
  ).toBeInTheDocument();
});
test("disabled button prevents duplicate actions", () => {
  const click = jest.fn();
  render(
    <Button disabled onClick={click}>
      Save
    </Button>,
  );
  fireEvent.click(screen.getByText("Save"));
  expect(click).not.toHaveBeenCalled();
});

test("empty and history components render supplied and default content", () => {
  render(
    <>
      <EmptyState />
      <EmptyState>No laundry records.</EmptyState>
      <HistoryTimeline
        items={[{ id: 1, from_status: "", to_status: "Approved", remarks: "Reviewed", actor: "warden", occurred_at: "2026-01-01T00:00:00Z" }]}
      />
    </>,
  );
  expect(screen.getByText("No records yet.")).toBeInTheDocument();
  expect(screen.getByText("No laundry records.")).toBeInTheDocument();
  expect(screen.getByText(/New.*Approved/)).toBeInTheDocument();
  expect(screen.getByText(/Reviewed/)).toBeInTheDocument();
});
