/** Roles page component. */

import { useState } from 'react';
import { PageLayout } from '../components/PageLayout';
import { RolesTable } from '../components/RolesTable';

/**
 * Roles page component.
 */
export function Roles() {
  const [filters, setFilters] = useState<{ name?: string }>({});

  return (
    <PageLayout title="Rôles" description="Gérer les rôles et permissions">
      <div className="mb-4">
        <div className="row g-3">
          <div className="col-md-4">
            <label htmlFor="filterName" className="form-label">
              Nom
            </label>
            <input
              id="filterName"
              type="text"
              className="form-control"
              value={filters.name || ''}
              onChange={(e) =>
                setFilters({ ...filters, name: e.target.value || undefined })
              }
              placeholder="Filtrer par nom"
            />
          </div>
          <div className="col-md-4 d-flex align-items-end">
            <button className="btn btn-secondary" onClick={() => setFilters({})}>
              Réinitialiser
            </button>
          </div>
        </div>
      </div>

      <RolesTable filters={filters} />
    </PageLayout>
  );
}
