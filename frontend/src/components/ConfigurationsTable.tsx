/** Configurations table component. */

import { useEffect, useState } from 'react';
import { configurationsApi, Configuration } from '../services/configurations';

interface ConfigurationsTableProps {
  filters?: {
    category?: string;
    key?: string;
  };
  onEdit?: (config: Configuration) => void;
  onDelete?: (configId: number) => void;
}

/**
 * Configurations table component with filters and pagination.
 */
export function ConfigurationsTable({
  filters = {},
  onEdit,
  onDelete,
}: ConfigurationsTableProps) {
  const [configurations, setConfigurations] = useState<Configuration[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 100,
    total: 0,
    pages: 1,
  });

  useEffect(() => {
    const fetchConfigurations = async () => {
      try {
        setLoading(true);
        const response = await configurationsApi.list({
          page,
          per_page: 100,
          ...filters,
        });
        setConfigurations(response.data?.configurations || []);
        setPagination(response.data?.pagination || pagination);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Failed to load configurations'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchConfigurations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, filters]);

  const handleDelete = async (configId: number) => {
    const config = configurations.find(c => c.id === configId);
    if (
      window.confirm(
        `Êtes-vous sûr de vouloir supprimer la configuration "${config?.key}" ?`
      )
    ) {
      try {
        await configurationsApi.delete(configId);
        setConfigurations(configurations.filter(c => c.id !== configId));
        if (onDelete) {
          onDelete(configId);
        }
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Failed to delete configuration'
        );
      }
    }
  };

  if (loading) {
    return (
      <div className="text-center">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    );
  }

  return (
    <div>
      <table className="table table-striped table-hover">
        <thead>
          <tr>
            <th>ID</th>
            <th>Key</th>
            <th>Value</th>
            <th>Category</th>
            <th>Description</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {configurations.length === 0 ? (
            <tr>
              <td colSpan={6} className="text-center text-muted">
                Aucune configuration trouvée
              </td>
            </tr>
          ) : (
            configurations.map(config => (
              <tr key={config.id}>
                <td>{config.id}</td>
                <td>
                  <code>{config.key}</code>
                </td>
                <td>
                  <code className="text-break">{config.value}</code>
                </td>
                <td>
                  {config.category ? (
                    <span className="badge bg-info">{config.category}</span>
                  ) : (
                    '-'
                  )}
                </td>
                <td>{config.description || '-'}</td>
                <td>
                  <button
                    className="btn btn-sm btn-outline-primary me-2"
                    onClick={() => onEdit && onEdit(config)}
                  >
                    Éditer
                  </button>
                  <button
                    className="btn btn-sm btn-outline-danger"
                    onClick={() => handleDelete(config.id)}
                  >
                    Supprimer
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>

      {pagination.pages > 1 && (
        <nav aria-label="Pagination">
          <ul className="pagination justify-content-center">
            <li className={`page-item ${page === 1 ? 'disabled' : ''}`}>
              <button className="page-link" onClick={() => setPage(page - 1)}>
                Précédent
              </button>
            </li>
            <li className="page-item active">
              <span className="page-link">
                Page {page} sur {pagination.pages}
              </span>
            </li>
            <li
              className={`page-item ${page >= pagination.pages ? 'disabled' : ''}`}
            >
              <button className="page-link" onClick={() => setPage(page + 1)}>
                Suivant
              </button>
            </li>
          </ul>
        </nav>
      )}
    </div>
  );
}
