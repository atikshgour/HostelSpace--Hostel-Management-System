/* Owner: Anvi Srinivas | US-17,US-21 | Dev sprint 1; 4–6 | SRS sprint 1; 6 | Reviewer: Arin Singh (pending) */
import { render, screen, fireEvent } from "@testing-library/react";
import Button from "./Button";
import StatusBadge from "./StatusBadge";
import DataTable from "./DataTable";
import FormField from "./FormField";
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
