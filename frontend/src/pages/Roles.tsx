/** Roles page component. */

import { useState, useEffect } from 'react';
import { PageLayout } from '../components/PageLayout';
import { RolesTable } from '../components/RolesTable';
import { RoleForm } from '../components/RoleForm';
import { Role } from '../services/roles';

/**
 * Roles page component with filters, table, and form.
 */
export function Roles() {
  const [filters, setFilters] = useState<{
    name?: string;
  }>({});
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [showForm, setShowForm] = useState(false);

  const handleCreate = () => {
    setSelectedRole(null);
    setShowForm(true);
  };

  const handleEdit = (role: Role) => {
    setSelectedRole(role);
    setShowForm(true);
  };

  const handleSave = (role: Role) => {
    setShowForm(false);
    setSelectedRole(null);
    // Table will refresh automatically via useEffect
  };

  const handleCancel = () => {
    setShowForm(false);
    setSelectedRole(null);
  };

  const handleDelete = () => {
    // Table will handle refresh automatically
  };

  if (showForm) {
    return (
      <PageLayout title={selectedRole ? 'Modifier Rôle' : 'Créer Rôle'} description="">
        <div className="card">
          <div className="card-header">
            <h2 className="h4 mb-0">
              {selectedRole ? 'Modifier Rôle' : 'Créer Rôle'}
            </h2>
          </div>
          <div className="card-body">
            <RoleForm
              role={selectedRole || undefined}
              onSave={handleSave}
              onCancel={handleCancel}
            />
          </div>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout title="Rôles" description="Gérer les rôles et permissions">
      <div className="mb-4 d-flex justify-content-between align-items-center">
        <h2 className="h4 mb-0">Rôles</h2>
        <button
          className="btn btn-primary"
          onClick={handleCreate}
          aria-label="Créer un rôle"
        >
          <i className="bi bi-plus-circle me-2" aria-hidden="true" />
          Créer
        </button>
      </div>

      <div className="mb-4">
        <div className="row g-3">
          <div className="col-md-6">
            <label htmlFor="filterName" className="form-label">
              Nom
            </label>
            <input
              id="filterName"
              type="text"
              className="form-control"
              value={filters.name || ''}
              onChange={e =>
                setFilters({
                  ...filters,
                  name: e.target.value || undefined,
                })
              }
              placeholder="Filtrer par nom"
              aria-label="Filtrer par nom"
            />
          </div>
          <div className="col-md-6 d-flex align-items-end">
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

      <RolesTable
        filters={filters}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </PageLayout>
  );
}
