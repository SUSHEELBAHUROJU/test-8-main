import React from 'react';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import { useDashboardData } from '../hooks/useDashboardData';
import RetailerStats from '../components/dashboard/RetailerStats';
import DuePayments from '../components/dashboard/DuePayments';
import TransactionHistory from '../components/dashboard/TransactionHistory';
import CreditStatus from '../components/dashboard/CreditStatus';
import PaymentModal from '../components/modals/PaymentModal';
import { dues } from '../services';

export default function RetailerDashboard() {
  const { stats, loading, error, refreshData } = useDashboardData();
  const [duePayments, setDuePayments] = React.useState([]);
  const [transactions, setTransactions] = React.useState([]);
  const [selectedPayment, setSelectedPayment] = React.useState(null);
  const [isPaymentModalOpen, setIsPaymentModalOpen] = React.useState(false);

  const loadDashboardData = async () => {
    try {
      const [duesData, transactionsData] = await Promise.all([
        dues.getAll(),
        dues.getTransactionHistory()
      ]);
      setDuePayments(duesData);
      setTransactions(transactionsData);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    }
  };

  React.useEffect(() => {
    loadDashboardData();
  }, []);

  const handlePayment = (payment: any) => {
    setSelectedPayment(payment);
    setIsPaymentModalOpen(true);
  };

  const handlePaymentComplete = async () => {
    setIsPaymentModalOpen(false);
    await Promise.all([
      loadDashboardData(),
      refreshData()
    ]);
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border-l-4 border-red-400 p-4">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Retailer Dashboard</h1>
          <p className="text-gray-600">Track your dues and payments</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-2">
            <CreditStatus
              creditLimit={stats?.creditLimit || 0}
              availableCredit={stats?.availableCredit || 0}
              creditScore={stats?.creditScore || 0}
              creditHistory={[]}
              isLoading={loading}
            />
          </div>
          <RetailerStats
            stats={{
              totalDue: stats?.totalDue || 0,
              dueToday: stats?.dueToday || 0,
              overdueAmount: stats?.overdueAmount || 0
            }}
            isLoading={loading}
          />
        </div>

        <div className="grid grid-cols-1 gap-6">
          <DuePayments
            payments={duePayments}
            onPayment={handlePayment}
            isLoading={loading}
          />

          <TransactionHistory
            transactions={transactions}
            isLoading={loading}
          />
        </div>

        <PaymentModal
          isOpen={isPaymentModalOpen}
          onClose={() => setIsPaymentModalOpen(false)}
          onSuccess={handlePaymentComplete}
          payment={selectedPayment}
        />
      </div>
    </DashboardLayout>
  );
}