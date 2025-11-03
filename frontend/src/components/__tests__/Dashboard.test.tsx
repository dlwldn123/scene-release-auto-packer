/** Tests for Dashboard component. */

import { render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { Dashboard } from '../../pages/Dashboard';
import * as api from '../../services/api';

vi.mock('../../services/api');

describe('Dashboard', () => {
  it('should display loading state initially', () => {
    vi.spyOn(api.dashboardApi, 'getStats').mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<Dashboard />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('should display dashboard stats when loaded', async () => {
    vi.spyOn(api.dashboardApi, 'getStats').mockResolvedValue({
      data: {
        total_releases: 10,
        total_jobs: 5,
        user_releases: 3,
        user_jobs: 2,
        user: {
          id: 1,
          username: 'testuser',
          email: 'test@example.com',
          active: true,
        },
      },
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Total Releases')).toBeInTheDocument();
      expect(screen.getByText('10')).toBeInTheDocument();
    });
  });

  it('should display error message on failure', async () => {
    vi.spyOn(api.dashboardApi, 'getStats').mockRejectedValue(
      new Error('Failed to load')
    );

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText(/failed to load/i)).toBeInTheDocument();
    });
  });
});
