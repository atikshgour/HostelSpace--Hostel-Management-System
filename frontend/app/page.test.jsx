// Owner: Atiksh | US-20 / TC-CICD-01 | Sprint 1
import { render, screen } from '@testing-library/react';
import Home from './page';

test('identifies the application and its implementation boundary', () => {
  render(<Home />);
  expect(screen.getByRole('heading', { name: 'HostelSpace' })).toBeInTheDocument();
  expect(screen.getByText(/awaiting implementation/)).toBeInTheDocument();
});
