/** UsersTable component tests. */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UsersTable } from '../UsersTable';
import { usersApi } from '../../services/users';

// Mock service
vi.mock('../../services/users');

describe('UsersTable', () => {
  const mockUsers = [
    {
      id: 1,
      username: 'user1',
      email: 'user1@test.com',
      active: true,
      roles: [{ id: 1, name: 'admin' }],
      groups: [{ id: 1, name: 'Group1' }],
      created_at: '2025-01-01T00:00:00',
    },
    {
      id: 2,
      username: 'user2',
      email: 'user2@test.com',
      active: false,
      roles: [],
      groups: [],
      created_at: '2025-01-02T00:00:00',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render loading state', async () => {
    vi.mocked(usersApi.list).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<UsersTable />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('should render users list', async () => {
    vi.mocked(usersApi.list).mockResolvedValue({
      data: {
        users: mockUsers,
        pagination: { page: 1, per_page: 20, total: 2, pages: 1 },
      },
    });

    render(<UsersTable />);

    await waitFor(() => {
      expect(screen.getByText('user1')).toBeInTheDocument();
      expect(screen.getByText('user2')).toBeInTheDocument();
    });

    expect(screen.getByText('user1@test.com')).toBeInTheDocument();
    expect(screen.getByText('user2@test.com')).toBeInTheDocument();
  });

  it('should display roles and groups', async () => {
    vi.mocked(usersApi.list).mockResolvedValue({
      data: {
        users: [mockUsers[0]],
        pagination: { page: 1, per_page: 20, total: 1, pages: 1 },
      },
    });

    render(<UsersTable />);

    await waitFor(() => {
      expect(screen.getByText('admin')).toBeInTheDocument();
      expect(screen.getByText('Group1')).toBeInTheDocument();
    });
  });

  it('should display active/inactive status', async () => {
    vi.mocked(usersApi.list).mockResolvedValue({
      data: {
        users: mockUsers,
        pagination: { page: 1, per_page: 20, total: 2, pages: 1 },
      },
    });

    render(<UsersTable />);

    await waitFor(() => {
      expect(screen.getByText('Actif')).toBeInTheDocument();
      expect(screen.getByText('Inactif')).toBeInTheDocument();
    });
  });

  it('should call onEdit when edit button is clicked', async () => {
    const user = userEvent.setup();
    const onEdit = vi.fn();

    vi.mocked(usersApi.list).mockResolvedValue({
      data: {
        users: [mockUsers[0]],
        pagination: { page: 1, per_page: 20, total: 1, pages: 1 },
      },
    });

    render(<UsersTable onEdit={onEdit} />);

    await waitFor(() => {
      expect(screen.getByText('user1')).toBeInTheDocument();
    });

    const editButton = screen.getByRole('button', { name: /éditer/i });
    await user.click(editButton);

    expect(onEdit).toHaveBeenCalledWith(mockUsers[0]);
  });

  it('should delete user with confirmation', async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    window.confirm = vi.fn(() => true);

    vi.mocked(usersApi.list).mockResolvedValue({
      data: {
        users: [mockUsers[0]],
        pagination: { page: 1, per_page: 20, total: 1, pages: 1 },
      },
    });
    vi.mocked(usersApi.delete).mockResolvedValue({
      data: { message: 'User deleted successfully' },
    });

    render(<UsersTable onDelete={onDelete} />);

    await waitFor(() => {
      expect(screen.getByText('user1')).toBeInTheDocument();
    });

    const deleteButton = screen.getByRole('button', { name: /supprimer/i });
    await user.click(deleteButton);

    await waitFor(() => {
      expect(usersApi.delete).toHaveBeenCalledWith(1);
      expect(onDelete).toHaveBeenCalledWith(1);
    });
  });

  it('should not delete user if confirmation is cancelled', async () => {
    const user = userEvent.setup();
    const onDelete = vi.fn();
    window.confirm = vi.fn(() => false);

    vi.mocked(usersApi.list).mockResolvedValue({
      data: {
        users: [mockUsers[0]],
        pagination: { page: 1, per_page: 20, total: 1, pages: 1 },
      },
    });

    render(<UsersTable onDelete={onDelete} />);

    await waitFor(() => {
      expect(screen.getByText('user1')).toBeInTheDocument();
    });

    const deleteButton = screen.getByRole('button', { name: /supprimer/i });
    await user.click(deleteButton);

    expect(usersApi.delete).not.toHaveBeenCalled();
    expect(onDelete).not.toHaveBeenCalled();
  });

  it('should display empty state when no users', async () => {
    vi.mocked(usersApi.list).mockResolvedValue({
      data: {
        users: [],
        pagination: { page: 1, per_page: 20, total: 0, pages: 0 },
      },
    });

    render(<UsersTable />);

    await waitFor(() => {
      expect(screen.getByText(/aucun utilisateur trouvé/i)).toBeInTheDocument();
    });
  });

  it('should display error message on load failure', async () => {
    vi.mocked(usersApi.list).mockRejectedValue(new Error('Failed to load users'));

    render(<UsersTable />);

    await waitFor(() => {
      expect(screen.getByText(/failed to load/i)).toBeInTheDocument();
    });
  });

  it('should apply filters', async () => {
    vi.mocked(usersApi.list).mockResolvedValue({
      data: {
        users: mockUsers,
        pagination: { page: 1, per_page: 20, total: 2, pages: 1 },
      },
    });

    const filters = { username: 'user1', role_id: 1 };
    render(<UsersTable filters={filters} />);

    await waitFor(() => {
      expect(usersApi.list).toHaveBeenCalledWith(
        expect.objectContaining({ username: 'user1', role_id: 1 })
      );
    });
  });
});
