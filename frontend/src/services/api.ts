/** API service for backend communication. */

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

export interface ApiResponse<T> {
  data?: T;
  message?: string;
}

/**
 * Get authorization token from localStorage.
 */
function getAuthToken(): string | null {
  return localStorage.getItem('access_token');
}

/**
 * API request with authentication.
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  // Don't set Content-Type for FormData (browser sets it automatically)
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ message: 'Request failed' }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Dashboard API.
 */
export const dashboardApi = {
  /**
   * Get dashboard statistics.
   */
  async getStats() {
    return apiRequest<{
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
    }>('/dashboard/stats');
  },
};

/**
 * Auth API.
 */
export const authApi = {
  /**
   * Login.
   */
  async login(username: string, password: string) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const error = await response
        .json()
        .catch(() => ({ message: 'Login failed' }));
      throw new Error(error.message || 'Login failed');
    }

    const data = await response.json();
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token || '');
    }
    return data;
  },

  /**
   * Logout.
   */
  async logout() {
    await apiRequest('/auth/logout', { method: 'POST' });
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  /**
   * Get current user.
   */
  async getCurrentUser() {
    return apiRequest<{
      user: { id: number; username: string; email: string };
    }>('/auth/me');
  },
};
