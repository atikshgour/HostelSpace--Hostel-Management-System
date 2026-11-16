// Owner: Atiksh Gour | US-14 | Sprint 4 | Reviewer: Anvi Srinivas
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import ManageComplaintsPage from './page';
import * as api from '../../../src/features/complaints/api';
jest.mock('../../../src/features/complaints/api');

const complaint = { id: 7, room: 'A-1', category_name: 'Synthetic repair', description: 'Synthetic light',
  status: 'Open', assigned_to: null, history: [{ id: 1, actor: 1, created_at: '2026-10-29T10:00:00Z',
    old_status: '', new_status: 'Open', remarks: 'Complaint submitted.', old_assigned_to: null, new_assigned_to: null }] };
function setup(canAssign = true, results = [complaint]) {
  api.listComplaints.mockResolvedValue({ results, can_assign: canAssign, next: null, previous: null });
  api.listMaintenanceStaff.mockResolvedValue([{ id: 3, username: 'synthetic-staff', first_name: '', last_name: '' }]);
}
beforeEach(() => { jest.resetAllMocks(); setup(); });

test('loads real data, assigns staff and advances with the displayed expected status', async () => {
  api.assignComplaint.mockResolvedValue({ ...complaint, assigned_to: 3 });
  api.advanceComplaint.mockResolvedValue({ ...complaint, assigned_to: 3, status: 'In Progress' });
  render(<ManageComplaintsPage />);
  expect(screen.getByRole('status')).toHaveTextContent('Loading');
  const card = await screen.findByRole('article');
  expect(within(card).getByText('Synthetic light')).toBeVisible();
  fireEvent.change(screen.getByLabelText('Maintenance Staff'), { target: { value: '3' } });
  fireEvent.change(screen.getByLabelText(/Remarks/), { target: { value: 'Synthetic assignment' } });
  fireEvent.click(screen.getByRole('button', { name: 'Assign staff' }));
  await waitFor(() => expect(api.assignComplaint).toHaveBeenCalledWith(7, { assigned_to: 3, remarks: 'Synthetic assignment' }));
  await screen.findByText('Complaint updated.');
  fireEvent.change(screen.getByLabelText(/Remarks/), { target: { value: 'Synthetic work started' } });
  fireEvent.click(screen.getByRole('button', { name: 'Mark In Progress' }));
  await waitFor(() => expect(api.advanceComplaint).toHaveBeenCalledWith(7, {
    expected_status: 'Open', status: 'In Progress', remarks: 'Synthetic work started',
  }));
  await screen.findByRole('heading', { name: /In Progress/ });
});

test('maintenance view omits assignment and resolved records have no update controls', async () => {
  setup(false, [{ ...complaint, status: 'Resolved', assigned_to: 3 }]);
  render(<ManageComplaintsPage />);
  await screen.findByRole('article');
  expect(screen.queryByRole('combobox')).not.toBeInTheDocument();
  expect(screen.queryByLabelText(/Remarks/)).not.toBeInTheDocument();
  expect(api.listMaintenanceStaff).not.toHaveBeenCalled();
  fireEvent.click(screen.getByText('History (1)'));
  expect(screen.getByText('Complaint submitted.')).toBeInTheDocument();
});

test('empty state and reload after a failed request', async () => {
  api.listComplaints.mockRejectedValueOnce(new Error('An active session is required.'));
  render(<ManageComplaintsPage />);
  expect(await screen.findByRole('alert')).toHaveTextContent('An active session');
  setup(false, []);
  fireEvent.click(screen.getByRole('button', { name: 'Reload complaints' }));
  expect(await screen.findByText('No complaints available.')).toBeVisible();
});

test('failed mutation retains remarks and shows a recoverable error', async () => {
  setup(false, [{ ...complaint, assigned_to: 3 }]);
  api.advanceComplaint.mockRejectedValue(new Error('Complaint changed'));
  render(<ManageComplaintsPage />);
  await screen.findByRole('article');
  fireEvent.change(screen.getByLabelText(/Remarks/), { target: { value: 'Synthetic retry remarks' } });
  fireEvent.click(screen.getByRole('button', { name: 'Mark In Progress' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Complaint changed');
  expect(screen.getByLabelText(/Remarks/)).toHaveValue('Synthetic retry remarks');
});

