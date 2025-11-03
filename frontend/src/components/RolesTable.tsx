/** Roles table component. */

import { useEffect, useState } from 'react';
import { rolesApi, Role } from '../services/roles';

interface RolesTableProps {
  filters?: {
    name?: string;
  };
  onEdit?: (role: Role) => void;
  onDelete?: (roleId: number) => void;
}

/**
 * Roles table component with filters and pagination.
 */
export function RolesTable({ filters = {}, onEdit, onDelete }: RolesTableProps) {
  const [roles, setRoles] = useState<Role[]>([]);
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
    const fetchRoles = async () => {
      try {
        setLoading(true);
        const response = await rolesApi.list({
          page,
          per_page: 20,
          ...filters,
        });
        setRoles(response.data?.roles || []);
        setPagination(response.data?.pagination || pagination);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load roles');
      } finally {
        setLoading(false);
      }
    };

    fetchRoles();
  }, [page, filters]);

  const handleDelete = async (roleId: number) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce rôle ?')) {
      try {
        await rolesApi.delete(roleId);
        setRoles(roles.filter((r) => r.id !== roleId));
        if (onDelete) {
          onDelete(roleId);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete role');
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
            <th>Description</th>
            <th>Permissions</th>
            <th>Utilisateurs</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {roles.length === 0 ? (
            <tr>
              <td colSpan={6} className="text-center text-muted">
                Aucun rôle trouvé
              </td>
            </tr>
          ) : (
            roles.map((role) => (
              <tr key={role.id}>
                <td>{role.id}</td>
                <td>{role.name}</td>
                <td>{role.description || '-'}</td>
                <td>
                  {role.permissions.length > 0
                    ? role.permissions.map((p) => (
                        <span key={p.id} className="badge bg-info me-1">
                          {p.name}
                        </span>
                      ))
                    : '-'}
                </td>
                <td>
                  <span className="badge bg-secondary">{role.users_count}</span>
                </td>
                <td>
                  <button
                    className="btn btn-sm btn-outline-primary me-2"
                    onClick={() => onEdit && onEdit(role)}
                  >
                    Éditer
                  </button>
                  <button
                    className="btn btn-sm btn-outline-danger"
                    onClick={() => handleDelete(role.id)}
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
