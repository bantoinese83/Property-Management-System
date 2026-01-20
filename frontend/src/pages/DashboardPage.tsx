import React from 'react';
import { useAuth } from '../context/AuthContext';
import Button from '../components/common/Button';
import Card from '../components/common/Card';

const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div style={{ padding: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Property Management Dashboard</h1>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span>Welcome, {user?.username}!</span>
          <Button variant="secondary" onClick={logout}>
            Logout
          </Button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
        <Card title="Properties" subtitle="Manage your property portfolio">
          <p>View and manage all your properties, track occupancy rates, and monitor financial performance.</p>
        </Card>

        <Card title="Tenants" subtitle="Tenant information and management">
          <p>Keep track of tenant details, contact information, and lease agreements.</p>
        </Card>

        <Card title="Leases" subtitle="Lease agreements and renewals">
          <p>Manage lease terms, track expiration dates, and handle renewals.</p>
        </Card>

        <Card title="Maintenance" subtitle="Maintenance requests and work orders">
          <p>Handle maintenance requests, assign work orders, and track completion.</p>
        </Card>

        <Card title="Payments" subtitle="Rent collection and financial tracking">
          <p>Process rent payments, track overdue amounts, and manage financial records.</p>
        </Card>

        <Card title="Accounting" subtitle="Financial reports and analytics">
          <p>Generate financial reports, track expenses, and analyze property performance.</p>
        </Card>
      </div>
    </div>
  );
};

export default DashboardPage;