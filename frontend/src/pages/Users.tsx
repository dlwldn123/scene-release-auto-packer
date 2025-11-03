/** Users page component. */

import { useState, useEffect } from 'react';
import { PageLayout } from '../components/PageLayout';
import { UsersTable } from '../components/UsersTable';
import { UserForm } from '../components/UserForm';
import { User } from '../services/users';
import { rolesApi } from '../services/roles';

/**
 * Users page component with filters, table, and form.
 */
export function Users() {
  const [filters, setFilters] = useState<{
    username?: string;
    email?: string;
    role_id?: number;
    active?: boolean;
  }>({});
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [roles, setRoles] = useState<Array<{ id: number; name: string }>>([]);

  // Load roles for filter
  useEffect(() => {
    const fetchRoles = async () => {
      try {
        const response = await rolesApi.list({ per_page: 100 });
        setRoles(response.data?.roles || []);
      } catch (err) {
        console.error('Failed to load roles:', err);
      }
    };
    fetchRoles();
  });

  const handleCreate = () => {
    setSelectedUser(null);
    setShowForm(true);
  };

  const handleEdit = (user: User) => {
    setSelectedUser(user);
    setShowForm(true);
  };

  const handleSave = (user: User) => {
    setShowForm(false);
    setSelectedUser(null);
    // Table will refresh automatically via useEffect
  };

  const handleCancel = () => {
    setShowForm(false);
    setSelectedUser(null);
  };

  const handleDelete = () => {
    // Table will handle refresh automatically
  };

  if (showForm) {
    return (
      <PageLayout title={selectedUser ? 'Modifier Utilisateur' : 'Créer Utilisateur'} description="">
        <div className="card">
          <div className="card-header">
            <h2 className="h4 mb-0">
              {selectedUser ? 'Modifier Utilisateur' : 'Créer Utilisateur'}
            </h2>
          </div>
          <div className="card-body">
            <UserForm
              user={selectedUser || undefined}
              onSave={handleSave}
              onCancel={handleCancel}
            />
          </div>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout title="Utilisateurs" description="Gérer les utilisateurs">
      <div className="mb-4 d-flex justify-content-between align-items-center">
        <h2 className="h4 mb-0">Utilisateurs</h2>
        <button
          className="btn btn-primary"
          onClick={handleCreate}
          aria-label="Créer un utilisateur"
        >
          <i className="bi bi-plus-circle me-2" aria-hidden="true" />
          Créer
        </button>
      </div>

      <div className="mb-4">
        <div className="row g-3">
          <div className="col-md-3">
            <label htmlFor="filterUsername" className="form-label">
              Username
            </label>
            <input
              id="filterUsername"
              type="text"
              className="form-control"
              value={filters.username || ''}
              onChange={e =>
                setFilters({
                  ...filters,
                  username: e.target.value || undefined,
                })
              }
              placeholder="Filtrer par username"
              aria-label="Filtrer par username"
            />
          </div>
          <div className="col-md-3">
            <label htmlFor="filterEmail" className="form-label">
              Email
            </label>
            <input
              id="filterEmail"
              type="text"
              className="form-control"
              value={filters.email || ''}
              onChange={e =>
                setFilters({ ...filters, email: e.target.value || undefined })
              }
              placeholder="Filtrer par email"
              aria-label="Filtrer par email"
            />
          </div>
          <div className="col-md-3">
            <label htmlFor="filterRole" className="form-label">
              Rôle
            </label>
            <select
              id="filterRole"
              className="form-select"
              value={filters.role_id || ''}
              onChange={e =>
                setFilters({
                  ...filters,
                  role_id: e.target.value ? parseInt(e.target.value) : undefined,
                })
              }
              aria-label="Filtrer par rôle"
            >
              <option value="">Tous les rôles</option>
              {roles.map(role => (
                <option key={role.id} value={role.id}>
                  {role.name}
                </option>
              ))}
            </select>
          </div>
          <div className="col-md-3">
            <label htmlFor="filterActive" className="form-label">
              Statut
            </label>
            <select
              id="filterActive"
              className="form-select"
              value={
                filters.active === undefined
                  ? ''
                  : filters.active
                  ? 'active'
                  : 'inactive'
              }
              onChange={e =>
                setFilters({
                  ...filters,
                  active:
                    e.target.value === ''
                      ? undefined
                      : e.target.value === 'active',
                })
              }
              aria-label="Filtrer par statut"
            >
              <option value="">Tous</option>
              <option value="active">Actif</option>
              <option value="inactive">Inactif</option>
            </select>
          </div>
        </div>
        <div className="row mt-3">
          <div className="col-12">
            <button
              className="btn btn-secondary"
              onClick={() => setFilters({})}
              aria-label="Réinitialiser les filtres"
            >
              Réinitialiser
            </button>
          </div>
        </div>
      </div>

      <UsersTable
        filters={filters}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </PageLayout>
  );
}
