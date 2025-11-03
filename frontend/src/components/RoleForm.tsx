/** Role form component for creating/editing roles. */

import { useEffect, useState } from 'react';
import { rolesApi, Role, CreateRoleData, UpdateRoleData } from '../services/roles';
import { permissionsApi, Permission } from '../services/permissions';

interface RoleFormProps {
  role?: Role | null;
  onSave?: (role: Role) => void;
  onCancel?: () => void;
}

/**
 * Role form component for creating or editing roles.
 */
export function RoleForm({ role, onSave, onCancel }: RoleFormProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [selectedPermissionIds, setSelectedPermissionIds] = useState<number[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isEditing] = useState(!!role);

  useEffect(() => {
    // Load permissions
    const fetchPermissions = async () => {
      try {
        const response = await permissionsApi.list();
        setPermissions(response.data?.permissions || []);
      } catch (err) {
        // Silently fail - permissions list might not be available yet
        console.warn('Failed to load permissions:', err);
        setPermissions([]);
      }
    };

    fetchPermissions();

    // Pre-fill form if editing
    if (role) {
      setName(role.name);
      setDescription(role.description || '');
      // Handle permissions which might be objects with id or just numbers
      setSelectedPermissionIds(
        role.permissions.map(p => (typeof p === 'object' ? p.id : p))
      );
    }
  }, [role]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (isEditing && role) {
        // Update role
        const updateData: UpdateRoleData = {
          name,
          description: description || undefined,
          permission_ids: selectedPermissionIds,
        };
        const response = await rolesApi.update(role.id, updateData);
        if (onSave) {
          onSave(response.data?.role!);
        }
      } else {
        // Create role
        const createData: CreateRoleData = {
          name,
          description: description || undefined,
          permission_ids: selectedPermissionIds,
        };
        const response = await rolesApi.create(createData);
        if (onSave) {
          onSave(response.data?.role!);
        }
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to save role'
      );
    } finally {
      setLoading(false);
    }
  };

  const handlePermissionToggle = (permissionId: number) => {
    setSelectedPermissionIds(prev => {
      if (prev.includes(permissionId)) {
        return prev.filter(id => id !== permissionId);
      } else {
        return [...prev, permissionId];
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
        <label htmlFor="name" className="form-label required">
          Nom
        </label>
        <input
          id="name"
          type="text"
          className="form-control"
          value={name}
          onChange={e => setName(e.target.value)}
          required
          disabled={loading}
          aria-required="true"
        />
      </div>

      <div className="mb-3">
        <label htmlFor="description" className="form-label">
          Description
        </label>
        <textarea
          id="description"
          className="form-control"
          rows={3}
          value={description}
          onChange={e => setDescription(e.target.value)}
          disabled={loading}
        />
      </div>

      <div className="mb-3">
        <label className="form-label">Permissions</label>
        {permissions.length === 0 ? (
          <div className="alert alert-info" role="status">
            Les permissions seront gérées via l'API backend.
          </div>
        ) : (
          <div className="border rounded p-3" style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {permissions.map(permission => (
              <div key={permission.id} className="form-check">
                <input
                  id={`permission-${permission.id}`}
                  type="checkbox"
                  className="form-check-input"
                  checked={selectedPermissionIds.includes(permission.id)}
                  onChange={() => handlePermissionToggle(permission.id)}
                  disabled={loading}
                />
                <label htmlFor={`permission-${permission.id}`} className="form-check-label">
                  {permission.resource}:{permission.action}
                </label>
              </div>
            ))}
          </div>
        )}
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
