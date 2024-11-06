import api from '../api';

export interface DashboardStats {
  totalOutstanding: number;
  activeRetailers: number;
  monthlySales: number;
  newRetailers: number;
  creditLimit: number;
  availableCredit: number;
  creditScore: number;
  totalDue: number;
  dueToday: number;
  overdueAmount: number;
}

export const dashboard = {
  getStats: async (): Promise<DashboardStats> => {
    try {
      const response = await api.get('/dashboard/stats/');
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      throw error;
    }
  },

  getAnalytics: async () => {
    try {
      const response = await api.get('/dashboard/analytics/');
      return response.data;
    } catch (error) {
      console.error('Error fetching analytics:', error);
      throw error;
    }
  }
};