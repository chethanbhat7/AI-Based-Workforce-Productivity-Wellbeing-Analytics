/**
 * Custom React hook for fetching dashboard data
 */
import { useState, useEffect } from 'react';
import { dashboardApi } from '../services/api';

interface DashboardData {
  communication: any;
  tasks: any;
  work_hours: any;
  performance: any;
}

interface WellbeingData {
  overall_score: number;
  categories: {
    mental_health: number;
    physical_health: number;
    work_life_balance: number;
    stress_management: number;
  };
  check_ins: number;
  streak_days: number;
  status: string;
}

interface ProductivityData {
  efficiency_score: number;
  metrics: any;
  insights: any[];
}

export const useDashboardData = (userId: string | null) => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    if (!userId) return;

    setLoading(true);
    setError(null);

    const response = await dashboardApi.getMemberOverview(userId);

    if (response.error) {
      setError(response.error);
      setLoading(false);
      return;
    }

    setData(response.data);
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
  }, [userId]);

  return { data, loading, error, refetch: fetchData };
};

export const useWellbeingData = (userId: string | null) => {
  const [data, setData] = useState<WellbeingData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    if (!userId) return;

    setLoading(true);
    setError(null);

    const response = await dashboardApi.getWellbeingProfile(userId);

    if (response.error) {
      setError(response.error);
      setLoading(false);
      return;
    }

    setData(response.data);
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
  }, [userId]);

  return { data, loading, error, refetch: fetchData };
};

export const useProductivityData = (userId: string | null, period: 'week' | 'month' = 'week') => {
  const [data, setData] = useState<ProductivityData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    if (!userId) return;

    setLoading(true);
    setError(null);

    const response = await dashboardApi.getProductivityMetrics(userId, period);

    if (response.error) {
      setError(response.error);
      setLoading(false);
      return;
    }

    setData(response.data);
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
  }, [userId, period]);

  return { data, loading, error, refetch: fetchData };
};

export const useRefreshData = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = async (userId: string, daysBack: number = 14) => {
    setLoading(true);
    setError(null);

    const response = await dashboardApi.refreshData(userId, daysBack);

    if (response.error) {
      setError(response.error);
      setLoading(false);
      return { success: false, error: response.error };
    }

    setLoading(false);
    return { success: true, data: response.data };
  };

  return { refresh, loading, error };
};
