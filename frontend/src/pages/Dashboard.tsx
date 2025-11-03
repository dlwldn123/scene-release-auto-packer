/** Dashboard page component. */

import { useEffect, useState } from 'react';
import { PageLayout } from '../components/PageLayout';
import { dashboardApi } from '../services/api';

interface DashboardStats {
  total_releases: number;
  total_jobs: number;
  user_releases: number;
  user_jobs: number;
  user: {
    id: number;
    username: string;
    email: string;
    active: boolean;
  };
}

/**
 * Dashboard page component.
 */
export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await dashboardApi.getStats();
        setStats(response.data || null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dashboard stats');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <PageLayout title="Dashboard">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </PageLayout>
    );
  }

  if (error) {
    return (
      <PageLayout title="Dashboard">
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout title="Dashboard" description="Vue d'ensemble de l'application">
      <div className="row">
        <div className="col-md-3 mb-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Total Releases</h5>
              <p className="card-text display-4">{stats?.total_releases || 0}</p>
            </div>
          </div>
        </div>
        <div className="col-md-3 mb-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Total Jobs</h5>
              <p className="card-text display-4">{stats?.total_jobs || 0}</p>
            </div>
          </div>
        </div>
        <div className="col-md-3 mb-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Mes Releases</h5>
              <p className="card-text display-4">{stats?.user_releases || 0}</p>
            </div>
          </div>
        </div>
        <div className="col-md-3 mb-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Mes Jobs</h5>
              <p className="card-text display-4">{stats?.user_jobs || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {stats?.user && (
        <div className="row mt-4">
          <div className="col-12">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">Informations utilisateur</h5>
                <p className="card-text">
                  <strong>Username:</strong> {stats.user.username}
                </p>
                <p className="card-text">
                  <strong>Email:</strong> {stats.user.email}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </PageLayout>
  );
}
