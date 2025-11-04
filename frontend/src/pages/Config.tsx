/** Config page component. */

import { useState } from 'react';
import { PageLayout } from '../components/PageLayout';
import { ConfigurationsTable } from '../components/ConfigurationsTable';
import { ConfigurationForm } from '../components/ConfigurationForm';
import { Configuration } from '../services/configurations';

/**
 * Config page component.
 */
export function Config() {
  const [filters, setFilters] = useState<{ category?: string; key?: string }>(
    {}
  );
  const [showForm, setShowForm] = useState(false);
  const [editingConfig, setEditingConfig] = useState<Configuration | null>(
    null
  );
  const [refreshKey, setRefreshKey] = useState(0);

  const handleCreate = () => {
    setEditingConfig(null);
    setShowForm(true);
  };

  const handleEdit = (config: Configuration) => {
    setEditingConfig(config);
    setShowForm(true);
  };

  const handleSave = () => {
    setShowForm(false);
    setEditingConfig(null);
    setRefreshKey(prev => prev + 1);
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingConfig(null);
  };

  return (
    <PageLayout title="Configurations" description="Gérer les configurations">
      {!showForm ? (
        <>
          <div className="mb-3 d-flex justify-content-between align-items-center">
            <h2 className="h4 mb-0">Liste des configurations</h2>
            <button className="btn btn-primary" onClick={handleCreate}>
              <span className="me-2">+</span>
              Nouvelle configuration
            </button>
          </div>

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
                  onChange={e =>
                    setFilters({
                      ...filters,
                      category: e.target.value || undefined,
                    })
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
                  onChange={e =>
                    setFilters({ ...filters, key: e.target.value || undefined })
                  }
                  placeholder="Filtrer par key"
                />
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

          <ConfigurationsTable
            key={refreshKey}
            filters={filters}
            onEdit={handleEdit}
          />
        </>
      ) : (
        <>
          <div className="mb-3">
            <button
              className="btn btn-link text-decoration-none"
              onClick={handleCancel}
            >
              ← Retour à la liste
            </button>
          </div>
          <div className="card">
            <div className="card-header">
              <h3 className="h5 mb-0">
                {editingConfig ? 'Éditer' : 'Créer'} une configuration
              </h3>
            </div>
            <div className="card-body">
              <ConfigurationForm
                configuration={editingConfig}
                onSave={handleSave}
                onCancel={handleCancel}
              />
            </div>
          </div>
        </>
      )}
    </PageLayout>
  );
}
