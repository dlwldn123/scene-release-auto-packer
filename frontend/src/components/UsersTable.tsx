/** Users table component. */

import { useEffect, useState } from 'react';
import { usersApi, User } from '../services/users';

interface UsersTableProps {
  filters?: {
    username?: string;
    email?: string;
    role_id?: number;
  };
  onEdit?: (user: User) => void;
  onDelete?: (userId: number) => void;
}

/**
 * Users table component with filters and pagination.
 */
export function UsersTable({ filters = {}, onEdit, onDelete }: UsersTableProps) {
  const [users, setUsers] = useState<User[]>([]);
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
    const fetchUsers = async () => {
      try {
        setLoading(true);
        const response = await usersApi.list({
          page,
          per_page: 20,
          ...filters,
        });
        setUsers(response.data?.users || []);
        setPagination(response.data?.pagination || pagination);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load users');
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, [page, filters]);

  const handleDelete = async (userId: number) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ?')) {
      try {
        await usersApi.delete(userId);
        setUsers(users.filter((u) => u.id !== userId));
        if (onDelete) {
          onDelete(userId);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete user');
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
            <th>Username</th>
            <th>Email</th>
            <th>Rôles</th>
            <th>Groupes</th>
            <th>Statut</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.length === 0 ? (
            <tr>
              <td colSpan={7} className="text-center text-muted">
                Aucun utilisateur trouvé
              </td>
            </tr>
          ) : (
            users.map((user) => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{user.username}</td>
                <td>{user.email}</td>
                <td>
                  {user.roles.length > 0
                    ? user.roles.map((r) => (
                        <span key={r.id} className="badge bg-primary me-1">
                          {r.name}
                        </span>
                      ))
                    : '-'}
                </td>
                <td>
                  {user.groups.length > 0
                    ? user.groups.map((g) => (
                        <span key={g.id} className="badge bg-secondary me-1">
                          {g.name}
                        </span>
                      ))
                    : '-'}
                </td>
                <td>
                  <span className={`badge bg-${user.active ? 'success' : 'danger'}`}>
                    {user.active ? 'Actif' : 'Inactif'}
                  </span>
                </td>
                <td>
                  <button
                    className="btn btn-sm btn-outline-primary me-2"
                    onClick={() => onEdit && onEdit(user)}
                  >
                    Éditer
                  </button>
                  <button
                    className="btn btn-sm btn-outline-danger"
                    onClick={() => handleDelete(user.id)}
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
