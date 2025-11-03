/** Releases table component. */

import { useEffect, useState } from 'react';
import { releasesApi } from '../services/releases';

interface Release {
  id: number;
  user_id: number;
  group_id?: number;
  release_type: string;
  status: string;
  created_at: string;
}

interface ReleasesTableProps {
  filters?: {
    release_type?: string;
    status?: string;
  };
}

/**
 * Releases table component with filters and pagination.
 */
export function ReleasesTable({ filters = {} }: ReleasesTableProps) {
  const [releases, setReleases] = useState<Release[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    pages: 1,
  });

  useEffect(() => {
    const fetchReleases = async () => {
      try {
        setLoading(true);
        const response = await releasesApi.list({
          page,
          per_page: 20,
          ...filters,
        });
        setReleases(response.data?.releases || []);
        setPagination(response.data?.pagination || pagination);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load releases');
      } finally {
        setLoading(false);
      }
    };

    fetchReleases();
  }, [page, filters]);

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
            <th>Type</th>
            <th>Status</th>
            <th>Créé le</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {releases.length === 0 ? (
            <tr>
              <td colSpan={5} className="text-center text-muted">
                Aucune release trouvée
              </td>
            </tr>
          ) : (
            releases.map((release) => (
              <tr key={release.id}>
                <td>{release.id}</td>
                <td>
                  <span className="badge bg-primary">{release.release_type}</span>
                </td>
                <td>
                  <span className={`badge bg-${release.status === 'completed' ? 'success' : 'warning'}`}>
                    {release.status}
                  </span>
                </td>
                <td>{new Date(release.created_at).toLocaleDateString()}</td>
                <td>
                  <button className="btn btn-sm btn-outline-primary me-2">Voir</button>
                  <button className="btn btn-sm btn-outline-danger">Supprimer</button>
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
            <li className={`page-item ${page >= pagination.pages ? 'disabled' : ''}`}>
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
