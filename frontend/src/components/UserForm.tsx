/** User form component for creating/editing users. */

import { useEffect, useState } from 'react';
import { usersApi, User, CreateUserData, UpdateUserData } from '../services/users';
import { rolesApi } from '../services/roles';

interface UserFormProps {
  user?: User | null;
  onSave?: (user: User) => void;
  onCancel?: () => void;
}

interface Role {
  id: number;
  name: string;
  description?: string;
}

/**
 * User form component for creating or editing users.
 */
export function UserForm({ user, onSave, onCancel }: UserFormProps) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [note, setNote] = useState('');
  const [active, setActive] = useState(true);
  const [selectedRoleIds, setSelectedRoleIds] = useState<number[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isEditing] = useState(!!user);

  useEffect(() => {
    // Load roles
    const fetchRoles = async () => {
      try {
        const response = await rolesApi.list({ per_page: 100 });
        setRoles(response.data?.roles || []);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Failed to load roles'
        );
      }
    };

    fetchRoles();

    // Pre-fill form if editing
    if (user) {
      setUsername(user.username);
      setEmail(user.email);
      setNote(user.note || '');
      setActive(user.active);
      setSelectedRoleIds(user.roles.map(r => r.id));
    }
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (isEditing && user) {
        // Update user
        const updateData: UpdateUserData = {
          username,
          email,
          note: note || undefined,
          active,
          role_ids: selectedRoleIds,
        };
        // Only include password if provided
        if (password) {
          updateData.password = password;
        }
        const response = await usersApi.update(user.id, updateData);
        if (onSave) {
          onSave(response.data?.user!);
        }
      } else {
        // Create user
        if (!password) {
          setError('Le mot de passe est requis pour créer un utilisateur');
          setLoading(false);
          return;
        }
        const createData: CreateUserData = {
          username,
          email,
          password,
        };
        const response = await usersApi.create(createData);
        if (onSave) {
          onSave(response.data?.user!);
        }
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to save user'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleRoleToggle = (roleId: number) => {
    setSelectedRoleIds(prev => {
      if (prev.includes(roleId)) {
        return prev.filter(id => id !== roleId);
      } else {
        return [...prev, roleId];
      }
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      <div className="mb-3">
        <label htmlFor="username" className="form-label required">
          Username
        </label>
        <input
          id="username"
          type="text"
          className="form-control"
          value={username}
          onChange={e => setUsername(e.target.value)}
          required
          disabled={loading}
          aria-required="true"
        />
      </div>

      <div className="mb-3">
        <label htmlFor="email" className="form-label required">
          Email
        </label>
        <input
          id="email"
          type="email"
          className="form-control"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
          disabled={loading}
          aria-required="true"
        />
      </div>

      <div className="mb-3">
        <label htmlFor="password" className="form-label">
          {isEditing ? 'Mot de passe (laisser vide pour ne pas changer)' : 'Mot de passe (requis)'}
        </label>
        <input
          id="password"
          type="password"
          className="form-control"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required={!isEditing}
          disabled={loading}
          aria-required={!isEditing}
          minLength={8}
        />
        {!isEditing && (
          <div className="form-text">
            Minimum 8 caractères
          </div>
        )}
      </div>

      <div className="mb-3">
        <label htmlFor="note" className="form-label">
          Note
        </label>
        <textarea
          id="note"
          className="form-control"
          rows={3}
          value={note}
          onChange={e => setNote(e.target.value)}
          disabled={loading}
        />
      </div>

      <div className="mb-3">
        <div className="form-check form-switch">
          <input
            id="active"
            type="checkbox"
            className="form-check-input"
            checked={active}
            onChange={e => setActive(e.target.checked)}
            disabled={loading}
          />
          <label htmlFor="active" className="form-check-label">
            Actif
          </label>
        </div>
      </div>

      <div className="mb-3">
        <label className="form-label">Rôles</label>
        <div className="border rounded p-3" style={{ maxHeight: '200px', overflowY: 'auto' }}>
          {roles.length === 0 ? (
            <p className="text-muted mb-0">Aucun rôle disponible</p>
          ) : (
            roles.map(role => (
              <div key={role.id} className="form-check">
                <input
                  id={`role-${role.id}`}
                  type="checkbox"
                  className="form-check-input"
                  checked={selectedRoleIds.includes(role.id)}
                  onChange={() => handleRoleToggle(role.id)}
                  disabled={loading}
                />
                <label htmlFor={`role-${role.id}`} className="form-check-label">
                  {role.name}
                  {role.description && (
                    <span className="text-muted ms-2 small">
                      ({role.description})
                    </span>
                  )}
                </label>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="d-flex justify-content-end gap-2">
        {onCancel && (
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onCancel}
            disabled={loading}
          >
            Annuler
          </button>
        )}
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading}
          aria-busy={loading}
        >
          {loading ? (
            <>
              <span
                className="spinner-border spinner-border-sm me-2"
                role="status"
                aria-hidden="true"
              />
              Enregistrement...
            </>
          ) : (
            isEditing ? 'Mettre à jour' : 'Créer'
          )}
        </button>
      </div>
    </form>
  );
}
