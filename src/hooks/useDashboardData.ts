import { useState, useEffect, useCallback } from 'react';
import { dashboard } from '../services/api/dashboard';
import { useWebSocket } from './useWebSocket';

export function useDashboardData() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const websocket = useWebSocket();

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboard.getStats();
      setStats(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
      console.error('Dashboard data error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();

    // Listen for real-time updates
    const handleDueUpdate = () => loadData();
    const handlePaymentUpdate = () => loadData();
    const handleCreditUpdate = () => loadData();

    websocket.addListener('due_created', handleDueUpdate);
    websocket.addListener('due_updated', handleDueUpdate);
    websocket.addListener('payment_made', handlePaymentUpdate);
    websocket.addListener('credit_limit_updated', handleCreditUpdate);

    return () => {
      websocket.removeListener('due_created', handleDueUpdate);
      websocket.removeListener('due_updated', handleDueUpdate);
      websocket.removeListener('payment_made', handlePaymentUpdate);
      websocket.removeListener('credit_limit_updated', handleCreditUpdate);
    };
  }, [loadData, websocket]);

  const refreshData = async () => {
    await loadData();
  };

  return { stats, loading, error, refreshData };
}