/** UserForm component tests. */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserForm } from '../UserForm';
import { usersApi } from '../../services/users';
import { rolesApi } from '../../services/roles';

// Mock services
vi.mock('../../services/users');
vi.mock('../../services/roles');

describe('UserForm', () => {
  const mockRoles = [
    { id: 1, name: 'admin', description: 'Administrator' },
    { id: 2, name: 'editor', description: 'Editor' },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(rolesApi.list).mockResolvedValue({
      data: { roles: mockRoles, pagination: { page: 1, per_page: 100, total: 2, pages: 1 } },
    });
  });

  it('should render create user form', async () => {
    render(<UserForm onSave={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/mot de passe/i)).toBeInTheDocument();
    });

    expect(screen.getByRole('button', { name: /créer/i })).toBeInTheDocument();
  });

  it('should render edit user form with pre-filled values', async () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@test.com',
      active: true,
      note: 'Test note',
      roles: [{ id: 1, name: 'admin' }],
      groups: [],
      created_at: '2025-01-01T00:00:00',
    };

    render(<UserForm user={mockUser} onSave={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByDisplayValue('testuser')).toBeInTheDocument();
      expect(screen.getByDisplayValue('test@test.com')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Test note')).toBeInTheDocument();
    });

    expect(screen.getByRole('button', { name: /mettre à jour/i })).toBeInTheDocument();
  });

  it('should require password for new user', async () => {
    const user = userEvent.setup();
    render(<UserForm onSave={vi.fn()} />);

    await waitFor(() => {
      const passwordInput = screen.getByLabelText(/mot de passe.*requis/i);
      expect(passwordInput).toBeRequired();
    });
  });

  it('should allow optional password for edit', async () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@test.com',
      active: true,
      roles: [],
      groups: [],
      created_at: '2025-01-01T00:00:00',
    };

    render(<UserForm user={mockUser} onSave={vi.fn()} />);

    await waitFor(() => {
      const passwordInput = screen.getByLabelText(/mot de passe.*vide/i);
      expect(passwordInput).not.toBeRequired();
    });
  });

  it('should call onSave when form is submitted (create)', async () => {
    const user = userEvent.setup();
    const onSave = vi.fn();

    vi.mocked(usersApi.create).mockResolvedValue({
      data: {
        user: {
          id: 1,
          username: 'newuser',
          email: 'new@test.com',
          active: true,
          roles: [],
          groups: [],
          created_at: '2025-01-01T00:00:00',
        },
      },
    });

    render(<UserForm onSave={onSave} />);

    await waitFor(() => {
      expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    });

    await user.type(screen.getByLabelText(/username/i), 'newuser');
    await user.type(screen.getByLabelText(/email/i), 'new@test.com');
    await user.type(screen.getByLabelText(/mot de passe/i), 'password123');

    await user.click(screen.getByRole('button', { name: /créer/i }));

    await waitFor(() => {
      expect(usersApi.create).toHaveBeenCalledWith({
        username: 'newuser',
        email: 'new@test.com',
        password: 'password123',
      });
      expect(onSave).toHaveBeenCalled();
    });
  });

  it('should call onSave when form is submitted (update)', async () => {
    const user = userEvent.setup();
    const onSave = vi.fn();

    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@test.com',
      active: true,
      roles: [{ id: 1, name: 'admin' }],
      groups: [],
      created_at: '2025-01-01T00:00:00',
    };

    vi.mocked(usersApi.update).mockResolvedValue({
      data: {
        user: {
          ...mockUser,
          username: 'updateduser',
        },
      },
    });

    render(<UserForm user={mockUser} onSave={onSave} />);

    await waitFor(() => {
      expect(screen.getByDisplayValue('testuser')).toBeInTheDocument();
    });

    await user.clear(screen.getByDisplayValue('testuser'));
    await user.type(screen.getByLabelText(/username/i), 'updateduser');

    await user.click(screen.getByRole('button', { name: /mettre à jour/i }));

    await waitFor(() => {
      expect(usersApi.update).toHaveBeenCalledWith(1, expect.objectContaining({
        username: 'updateduser',
      }));
      expect(onSave).toHaveBeenCalled();
    });
  });

  it('should toggle role selection', async () => {
    const user = userEvent.setup();
    render(<UserForm onSave={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByLabelText(/admin/i)).toBeInTheDocument();
    });

    const adminCheckbox = screen.getByLabelText(/admin/i);
    expect(adminCheckbox).not.toBeChecked();

    await user.click(adminCheckbox);
    expect(adminCheckbox).toBeChecked();

    await user.click(adminCheckbox);
    expect(adminCheckbox).not.toBeChecked();
  });

  it('should call onCancel when cancel button is clicked', async () => {
    const user = userEvent.setup();
    const onCancel = vi.fn();

    render(<UserForm onSave={vi.fn()} onCancel={onCancel} />);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /annuler/i })).toBeInTheDocument();
    });

    await user.click(screen.getByRole('button', { name: /annuler/i }));
    expect(onCancel).toHaveBeenCalled();
  });

  it('should display error message on save failure', async () => {
    const user = userEvent.setup();
    vi.mocked(usersApi.create).mockRejectedValue(new Error('Username already exists'));

    render(<UserForm onSave={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    });

    await user.type(screen.getByLabelText(/username/i), 'testuser');
    await user.type(screen.getByLabelText(/email/i), 'test@test.com');
    await user.type(screen.getByLabelText(/mot de passe/i), 'password123');

    await user.click(screen.getByRole('button', { name: /créer/i }));

    await waitFor(() => {
      expect(screen.getByText(/failed to save|username already exists/i)).toBeInTheDocument();
    });
  });
});
