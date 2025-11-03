/** Rules table component. */

import { useEffect, useState } from 'react';
import { rulesApi, Rule } from '../services/rules';

interface RulesTableProps {
  filters?: {
    scene?: string;
    section?: string;
    year?: number;
  };
  onEdit?: (rule: Rule) => void;
  onDelete?: (ruleId: number) => void;
}

/**
 * Rules table component with filters and pagination.
 */
export function RulesTable({ filters = {}, onEdit, onDelete }: RulesTableProps) {
  const [rules, setRules] = useState<Rule[]>([]);
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
    const fetchRules = async () => {
      try {
        setLoading(true);
        const response = await rulesApi.list({
          page,
          per_page: 20,
          ...filters,
        });
        setRules(response.data?.rules || []);
        setPagination(response.data?.pagination || pagination);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load rules');
      } finally {
        setLoading(false);
      }
    };

    fetchRules();
  }, [page, filters]);

  const handleDelete = async (ruleId: number) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette règle ?')) {
      try {
        await rulesApi.delete(ruleId);
        setRules(rules.filter((r) => r.id !== ruleId));
        if (onDelete) {
          onDelete(ruleId);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete rule');
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
            <th>Nom</th>
            <th>Scene</th>
            <th>Section</th>
            <th>Année</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {rules.length === 0 ? (
            <tr>
              <td colSpan={6} className="text-center text-muted">
                Aucune règle trouvée
              </td>
            </tr>
          ) : (
            rules.map((rule) => (
              <tr key={rule.id}>
                <td>{rule.id}</td>
                <td>{rule.name}</td>
                <td>{rule.scene || '-'}</td>
                <td>{rule.section || '-'}</td>
                <td>{rule.year || '-'}</td>
                <td>
                  <button
                    className="btn btn-sm btn-outline-primary me-2"
                    onClick={() => onEdit && onEdit(rule)}
                  >
                    Éditer
                  </button>
                  <button
                    className="btn btn-sm btn-outline-danger"
                    onClick={() => handleDelete(rule.id)}
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
