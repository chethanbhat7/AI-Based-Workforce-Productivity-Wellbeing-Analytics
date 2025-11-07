/**
 * API Service for Workforce Wellbeing Analytics
 * Connects frontend to backend endpoints
 */

// Use environment variable or default to localhost
const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        error: data.detail || 'An error occurred',
        status: response.status,
      };
    }

    return {
      data,
      status: response.status,
    };
  } catch (error) {
    console.error('API Error:', error);
    return {
      error: error instanceof Error ? error.message : 'Network error',
      status: 500,
    };
  }
}

/**
 * Dashboard API endpoints
 */
export const dashboardApi = {
  /**
   * Get member dashboard overview
   */
  getMemberOverview: async (userId: string) => {
    return apiFetch<any>(`/dashboard/member/${userId}/overview`);
  },

  /**
   * Get wellbeing profile
   */
  getWellbeingProfile: async (userId: string) => {
    return apiFetch<any>(`/dashboard/member/${userId}/wellbeing`);
  },

  /**
   * Get productivity metrics
   */
  getProductivityMetrics: async (userId: string, period: 'week' | 'month' = 'week') => {
    return apiFetch<any>(`/dashboard/member/${userId}/metrics?period=${period}`);
  },

  /**
   * Refresh dashboard data (fetch fresh data from APIs)
   */
  refreshData: async (userId: string, daysBack: number = 14) => {
    return apiFetch<any>(`/dashboard/member/${userId}/refresh`, {
      method: 'POST',
      body: JSON.stringify({ days_back: daysBack }),
    });
  },

  /**
   * Get team overview for supervisor
   */
  getTeamOverview: async (supervisorId: string, teamIds?: string[]) => {
    const teamIdsParam = teamIds ? `?team_ids=${teamIds.join(',')}` : '';
    return apiFetch<any>(`/dashboard/supervisor/team-overview?supervisor_id=${supervisorId}${teamIdsParam}`);
  },
};

/**
 * Feature extraction API endpoints
 */
export const featureApi = {
  /**
   * Extract features for a user
   */
  extractFeatures: async (userId: string, daysBack: number = 14, providers?: string[]) => {
    return apiFetch<any>(`/features/extract/${userId}`, {
      method: 'POST',
      body: JSON.stringify({
        days_back: daysBack,
        providers: providers || ['microsoft', 'slack', 'jira'],
      }),
    });
  },

  /**
   * Get latest features
   */
  getLatestFeatures: async (userId: string) => {
    return apiFetch<any>(`/features/user/${userId}/latest`);
  },

  /**
   * Get feature history
   */
  getFeatureHistory: async (userId: string, daysBack: number = 30) => {
    return apiFetch<any>(`/features/user/${userId}/history?days_back=${daysBack}`);
  },
};

/**
 * Data fetching API endpoints
 */
export const dataApi = {
  /**
   * Fetch Microsoft data
   */
  fetchMicrosoft: async (userId: string, dataTypes: string[], daysBack: number = 14) => {
    return apiFetch<any>('/data/microsoft/fetch', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        data_types: dataTypes,
        days_back: daysBack,
      }),
    });
  },

  /**
   * Fetch Slack data
   */
  fetchSlack: async (userId: string, dataTypes: string[], daysBack: number = 14) => {
    return apiFetch<any>('/data/slack/fetch', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        data_types: dataTypes,
        days_back: daysBack,
      }),
    });
  },

  /**
   * Fetch Jira data
   */
  fetchJira: async (userId: string, dataTypes: string[], daysBack: number = 14) => {
    return apiFetch<any>('/data/jira/fetch', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        data_types: dataTypes,
        days_back: daysBack,
      }),
    });
  },

  /**
   * Get fetch history
   */
  getFetchHistory: async (userId: string, provider?: string) => {
    const providerParam = provider ? `?provider=${provider}` : '';
    return apiFetch<any>(`/data/fetch-history/${userId}${providerParam}`);
  },
};

/**
 * Authentication API endpoints
 */
export const authApi = {
  /**
   * Get OAuth authorization URL
   */
  getAuthUrl: async (provider: string, userId: string) => {
    return apiFetch<{ auth_url: string }>(`/auth/${provider}/login?user_id=${userId}`);
  },

  /**
   * Check connection status
   */
  getConnectionStatus: async (userId: string) => {
    return apiFetch<any>(`/users/${userId}/connections`);
  },
};

/**
 * User API endpoints
 */
export const userApi = {
  /**
   * Get user profile
   */
  getProfile: async (userId: string) => {
    return apiFetch<any>(`/users/${userId}`);
  },

  /**
   * Update user profile
   */
  updateProfile: async (userId: string, data: any) => {
    return apiFetch<any>(`/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },
};

/**
 * Health check endpoint
 */
export const healthCheck = async () => {
  return apiFetch<any>('/health');
};

export default {
  dashboardApi,
  featureApi,
  dataApi,
  authApi,
  userApi,
  healthCheck,
};
