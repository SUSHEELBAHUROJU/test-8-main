import api from '../api';

export interface Due {
  id: string;
  supplier: {
    id: string;
    business_name: string;
    phone: string;
  };
  retailer: {
    id: string;
    business_name: string;
    phone: string;
  };
  amount: number;
  description: string;
  purchase_date: string;
  due_date: string;
  status: 'pending' | 'paid' | 'overdue';
  created_at: string;
  updated_at: string;
}

export interface Payment {
  id: string;
  due: string;
  amount: number;
  payment_method: string;
  payment_date: string;
  reference_id?: string;
  status: 'pending' | 'completed' | 'failed';
}

export const dues = {
  getAll: async (): Promise<Due[]> => {
    try {
      const response = await api.get('/dues/');
      return response.data;
    } catch (error) {
      console.error('Error fetching dues:', error);
      throw error;
    }
  },

  create: async (data: {
    retailer: string;
    amount: number;
    description: string;
    purchase_date: string;
    due_date: string;
  }): Promise<Due> => {
    try {
      const response = await api.post('/dues/', data);
      return response.data;
    } catch (error) {
      console.error('Error creating due:', error);
      throw error;
    }
  },

  makePayment: async (dueId: string, data: {
    amount: number;
    payment_method: string;
    reference_id?: string;
  }): Promise<Payment> => {
    try {
      const response = await api.post(`/dues/${dueId}/pay/`, data);
      return response.data;
    } catch (error) {
      console.error('Error making payment:', error);
      throw error;
    }
  },

  getTransactionHistory: async () => {
    try {
      const response = await api.get('/dues/transactions/');
      return response.data;
    } catch (error) {
      console.error('Error fetching transaction history:', error);
      throw error;
    }
  },

  getDueDetails: async (dueId: string): Promise<Due> => {
    try {
      const response = await api.get(`/dues/${dueId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching due details:', error);
      throw error;
    }
  },

  // Get payment history for a specific due
  getPaymentHistory: async (dueId: string): Promise<Payment[]> => {
    try {
      const response = await api.get(`/dues/${dueId}/payments/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching payment history:', error);
      throw error;
    }
  }
};