/** Users page component. */

import { useState } from 'react';
import { PageLayout } from '../components/PageLayout';
import { UsersTable } from '../components/UsersTable';

/**
 * Users page component.
 */
export function Users() {
  const [filters, setFilters] = useState<{
    username?: string;
    email?: string;
    role_id?: number;
  }>({});

  return (
    <PageLayout title="Utilisateurs" description="Gérer les utilisateurs">
      <div className="mb-4">
        <div className="row g-3">
          <div className="col-md-4">
            <label htmlFor="filterUsername" className="form-label">
              Username
            </label>
            <input
              id="filterUsername"
              type="text"
              className="form-control"
              value={filters.username || ''}
              onChange={(e) =>
                setFilters({ ...filters, username: e.target.value || undefined })
              }
              placeholder="Filtrer par username"
            />
          </div>
          <div className="col-md-4">
            <label htmlFor="filterEmail" className="form-label">
              Email
            </label>
            <input
              id="filterEmail"
              type="text"
              className="form-control"
              value={filters.email || ''}
              onChange={(e) =>
                setFilters({ ...filters, email: e.target.value || undefined })
              }
              placeholder="Filtrer par email"
            />
          </div>
          <div className="col-md-4 d-flex align-items-end">
            <button className="btn btn-secondary" onClick={() => setFilters({})}>
              Réinitialiser
            </button>
          </div>
        </div>
      </div>

      <UsersTable filters={filters} />
    </PageLayout>
  );
}
