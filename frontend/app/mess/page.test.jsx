// Owner: Atiksh Gour | US-15 / TC-FR08-01 | Sprint 5 | Reviewer: Anvi Srinivas
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import MyMessPage from './page';
import ManageMessPage from './manage/page';
import * as api from '../../src/features/mess/api';
jest.mock('../../src/features/mess/api');

const allocation = { id: 8, student: 3, mess_name: 'Synthetic mess', valid_from: '2026-10-29',
  valid_until: '2026-10-29', is_active: true, version: 1 };
const coupon = { id: 9, allocation: 8, code: 'SYNTHETIC-VALID', valid_from: '2026-10-29',
  valid_until: '2026-10-29', is_active: true, version: 1 };
beforeEach(() => {
  jest.resetAllMocks();
  api.getMyMess.mockResolvedValue({ as_of: '2026-10-29', timezone: 'Asia/Kolkata', allocation, coupons: [coupon] });
  api.getMessManagement.mockResolvedValue({ students: [{ id: 3, username: 'synthetic-student' }], allocations: [], coupons: [] });
});

test('student sees backend allocation/coupons and no write controls', async () => {
  render(<MyMessPage />);
  expect(screen.getByRole('status')).toHaveTextContent('Loading');
  expect(await screen.findByText('Synthetic mess')).toBeVisible();
  expect(screen.getByText('SYNTHETIC-VALID')).toBeVisible();
  expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
  expect(screen.queryByRole('button', { name: /order|redeem/i })).not.toBeInTheDocument();
});

test('empty personal records are explicit', async () => {
  api.getMyMess.mockResolvedValue({ as_of: '2026-10-29', timezone: 'Asia/Kolkata', allocation: null, coupons: [] });
  render(<MyMessPage />);
  expect(await screen.findByText('No current active mess allocation.')).toBeVisible();
  expect(screen.getByText('No currently valid coupons.')).toBeVisible();
});

test('failed load can be retried', async () => {
  api.getMyMess.mockRejectedValueOnce(new Error('Session required.'));
  render(<MyMessPage />);
  expect(await screen.findByRole('alert')).toHaveTextContent('Session required.');
  fireEvent.click(screen.getByRole('button', { name: 'Reload records' }));
  expect(await screen.findByText('Synthetic mess')).toBeVisible();
});

function fillDates(form) {
  fireEvent.change(within(form).getByLabelText('Valid from'), { target: { value: '2026-10-29' } });
  fireEvent.change(within(form).getByLabelText('Valid until'), { target: { value: '2026-10-29' } });
}

test('staff creates an allocation and coupon from server IDs', async () => {
  api.saveAllocation.mockResolvedValue(allocation);
  api.saveCoupon.mockResolvedValue(coupon);
  render(<ManageMessPage />);
  const form = await screen.findByRole('form', { name: 'Create allocation' });
  fireEvent.change(within(form).getByLabelText('Student'), { target: { value: '3' } });
  fireEvent.change(within(form).getByLabelText('Mess name'), { target: { value: ' Synthetic mess ' } });
  fillDates(form);
  fireEvent.submit(form);
  await waitFor(() => expect(api.saveAllocation).toHaveBeenCalledWith(undefined, {
    student: 3, mess_name: 'Synthetic mess', valid_from: '2026-10-29', valid_until: '2026-10-29', is_active: true,
  }));
  await screen.findByRole('form', { name: 'Edit allocation 8' });
  const coupons = screen.getByRole('form', { name: 'Create coupon' });
  fireEvent.change(within(coupons).getByLabelText('Allocation'), { target: { value: '8' } });
  fireEvent.change(within(coupons).getByLabelText('Coupon code'), { target: { value: 'SYNTHETIC-VALID' } });
  fillDates(coupons);
  fireEvent.submit(coupons);
  await screen.findByRole('form', { name: 'Edit coupon 9' });
  expect(api.saveCoupon).toHaveBeenCalledWith(undefined, {
    allocation: 8, code: 'SYNTHETIC-VALID', valid_from: '2026-10-29', valid_until: '2026-10-29', is_active: true,
  });
});

test('staff edits carry expected version and show rejected writes without losing input', async () => {
  api.getMessManagement.mockResolvedValue({ students: [], allocations: [allocation], coupons: [coupon] });
  api.saveCoupon.mockRejectedValueOnce(new Error('Record changed.'));
  render(<ManageMessPage />);
  const form = await screen.findByRole('form', { name: 'Edit coupon 9' });
  fireEvent.click(within(form).getByLabelText('Active'));
  fireEvent.submit(form);
  expect(await screen.findByRole('alert')).toHaveTextContent('Record changed.');
  expect(within(form).getByLabelText('Active')).not.toBeChecked();
  expect(api.saveCoupon).toHaveBeenCalledWith(9, {
    code: coupon.code, valid_from: '2026-10-29', valid_until: '2026-10-29', is_active: false, expected_version: 1,
  });
});

test('invalid date range is rejected before writing', async () => {
  render(<ManageMessPage />);
  const form = await screen.findByRole('form', { name: 'Create allocation' });
  fireEvent.change(within(form).getByLabelText('Mess name'), { target: { value: 'Synthetic' } });
  fillDates(form);
  fireEvent.change(within(form).getByLabelText('Valid until'), { target: { value: '2026-10-28' } });
  fireEvent.submit(form);
  expect(await screen.findByRole('alert')).toHaveTextContent('Valid until must be on or after valid from.');
  expect(api.saveAllocation).not.toHaveBeenCalled();
});
