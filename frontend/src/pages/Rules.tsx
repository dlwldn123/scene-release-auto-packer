/** Rules page component. */

import { useState } from 'react';
import { PageLayout } from '../components/PageLayout';
import { RulesTable } from '../components/RulesTable';
import { Rule } from '../services/rules';

/**
 * Rules page component.
 */
export function Rules() {
  const [filters, setFilters] = useState<{ scene?: string; section?: string; year?: number }>({});
  const [selectedRule, setSelectedRule] = useState<Rule | null>(null);

  return (
    <PageLayout title="Règles" description="Gérer les règles Scene">
      <div className="mb-4">
        <div className="row g-3">
          <div className="col-md-4">
            <label htmlFor="filterScene" className="form-label">
              Scene
            </label>
            <input
              id="filterScene"
              type="text"
              className="form-control"
              value={filters.scene || ''}
              onChange={(e) =>
                setFilters({ ...filters, scene: e.target.value || undefined })
              }
              placeholder="Filtrer par scene"
            />
          </div>
          <div className="col-md-4">
            <label htmlFor="filterSection" className="form-label">
              Section
            </label>
            <input
              id="filterSection"
              type="text"
              className="form-control"
              value={filters.section || ''}
              onChange={(e) =>
                setFilters({ ...filters, section: e.target.value || undefined })
              }
              placeholder="Filtrer par section"
            />
          </div>
          <div className="col-md-4">
            <label htmlFor="filterYear" className="form-label">
              Année
            </label>
            <input
              id="filterYear"
              type="number"
              className="form-control"
              value={filters.year || ''}
              onChange={(e) =>
                setFilters({
                  ...filters,
                  year: e.target.value ? parseInt(e.target.value, 10) : undefined,
                })
              }
              placeholder="Filtrer par année"
            />
          </div>
        </div>
        <div className="mt-3">
          <button className="btn btn-secondary" onClick={() => setFilters({})}>
            Réinitialiser
          </button>
        </div>
      </div>

      <RulesTable
        filters={filters}
        onEdit={(rule) => setSelectedRule(rule)}
        onDelete={() => setSelectedRule(null)}
      />

      {selectedRule && (
        <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">{selectedRule.name}</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setSelectedRule(null)}
                ></button>
              </div>
              <div className="modal-body">
                <pre className="bg-light p-3 rounded" style={{ maxHeight: '400px', overflow: 'auto' }}>
                  {selectedRule.content}
                </pre>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setSelectedRule(null)}
                >
                  Fermer
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </PageLayout>
  );
}
