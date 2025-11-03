/** Releases list page component. */

import { useState } from 'react';
import { PageLayout } from '../components/PageLayout';
import { ReleasesTable } from '../components/ReleasesTable';

/**
 * Releases list page component.
 */
export function ReleasesList() {
  const [filters, setFilters] = useState<{ release_type?: string; status?: string }>({});

  return (
    <PageLayout title="Liste des Releases" description="Gérer toutes les releases">
      <div className="mb-4">
        <div className="row g-3">
          <div className="col-md-4">
            <label htmlFor="filterType" className="form-label">
              Type de Release
            </label>
            <select
              id="filterType"
              className="form-select"
              value={filters.release_type || ''}
              onChange={(e) =>
                setFilters({ ...filters, release_type: e.target.value || undefined })
              }
            >
              <option value="">Tous</option>
              <option value="EBOOK">EBOOK</option>
              <option value="TV">TV</option>
              <option value="DOCS">DOCS</option>
            </select>
          </div>
          <div className="col-md-4">
            <label htmlFor="filterStatus" className="form-label">
              Statut
            </label>
            <select
              id="filterStatus"
              className="form-select"
              value={filters.status || ''}
              onChange={(e) => setFilters({ ...filters, status: e.target.value || undefined })}
            >
              <option value="">Tous</option>
              <option value="draft">Brouillon</option>
              <option value="completed">Complété</option>
              <option value="processing">En traitement</option>
            </select>
          </div>
          <div className="col-md-4 d-flex align-items-end">
            <button
              className="btn btn-secondary"
              onClick={() => setFilters({})}
            >
              Réinitialiser
            </button>
          </div>
        </div>
      </div>

      <ReleasesTable filters={filters} />
    </PageLayout>
  );
}
