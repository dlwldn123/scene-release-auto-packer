/** Config page component. */

import { useState } from 'react';
import { PageLayout } from '../components/PageLayout';
import { ConfigurationsTable } from '../components/ConfigurationsTable';

/**
 * Config page component.
 */
export function Config() {
  const [filters, setFilters] = useState<{ category?: string; key?: string }>({});

  return (
    <PageLayout title="Configurations" description="Gérer les configurations">
      <div className="mb-4">
        <div className="row g-3">
          <div className="col-md-4">
            <label htmlFor="filterCategory" className="form-label">
              Catégorie
            </label>
            <input
              id="filterCategory"
              type="text"
              className="form-control"
              value={filters.category || ''}
              onChange={(e) =>
                setFilters({ ...filters, category: e.target.value || undefined })
              }
              placeholder="Filtrer par catégorie"
            />
          </div>
          <div className="col-md-4">
            <label htmlFor="filterKey" className="form-label">
              Key
            </label>
            <input
              id="filterKey"
              type="text"
              className="form-control"
              value={filters.key || ''}
              onChange={(e) =>
                setFilters({ ...filters, key: e.target.value || undefined })
              }
              placeholder="Filtrer par key"
            />
          </div>
          <div className="col-md-4 d-flex align-items-end">
            <button className="btn btn-secondary" onClick={() => setFilters({})}>
              Réinitialiser
            </button>
          </div>
        </div>
      </div>

      <ConfigurationsTable filters={filters} />
    </PageLayout>
  );
}
