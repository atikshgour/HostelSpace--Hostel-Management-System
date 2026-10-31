// Owner: Atiksh Gour | US-16 | Sprint 5 | Reviewer: Anvi Srinivas
import { render, screen } from '@testing-library/react';
import FeesPanel from '../../src/features/fees/FeesPanel';
import { getFees } from '../../src/features/fees/api';

jest.mock('../../src/features/fees/api', () => ({ getFees: jest.fn(), initiateFee: jest.fn(), verifyAttempt: jest.fn() }));

test('shows owned dues and blocks paid initiation', async () => {
  getFees.mockResolvedValue({ results: [
    { id: 1, description: 'Synthetic hostel fee', amount: '125.50', currency: 'INR',
      status: 'Paid', attempts: [{ id: 4, status: 'Succeeded', created_at: '2026-10-31T00:00:00Z' }] },
  ] });
  render(<FeesPanel />);
  expect(await screen.findByText('Synthetic hostel fee')).toBeInTheDocument();
  expect(screen.getByText('INR 125.50 — Paid')).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: /pay in test mode/i })).not.toBeInTheDocument();
});

test('shows empty state', async () => {
  getFees.mockResolvedValue({ results: [] });
  render(<FeesPanel />);
  expect(await screen.findByText('No fees are currently due.')).toBeInTheDocument();
});
