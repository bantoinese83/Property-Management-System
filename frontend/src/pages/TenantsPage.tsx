import React, { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { API_ENDPOINTS } from '../api/endpoints';
import { Tenant } from '../types/models';
import Button from '../components/common/Button';
import Card from '../components/common/Card';
import Modal from '../components/common/Modal';
import TenantForm from '../components/tenants/TenantForm';
import '../styles/pages/TenantsPage.css';

interface TenantsResponse {
  results: Tenant[];
  count: number;
  next?: string;
  previous?: string;
}

const TenantsPage: React.FC = () => {
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingTenant, setEditingTenant] = useState<Tenant | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const { data, loading, error, refetch } = useApi<TenantsResponse>(
    `${API_ENDPOINTS.TENANTS.LIST}?search=${searchTerm}`
  );

  const tenants = data?.results || [];

  const handleAddTenant = () => {
    setShowAddModal(true);
  };

  const handleEditTenant = (tenant: Tenant) => {
    setEditingTenant(tenant);
  };

  const handleCloseModal = () => {
    setShowAddModal(false);
    setEditingTenant(null);
    refetch(); // Refresh the list
  };

  const handleDeleteTenant = async (tenantId: number) => {
    if (window.confirm('Are you sure you want to delete this tenant?')) {
      try {
        const response = await fetch(`${API_ENDPOINTS.TENANTS.LIST}${tenantId}/`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
        });

        if (response.ok) {
          refetch(); // Refresh the list
        } else {
          alert('Failed to delete tenant');
        }
      } catch (error) {
        alert('Error deleting tenant');
      }
    }
  };

  if (loading) return <div className="loading">Loading tenants...</div>;
  if (error) return <div className="error">Error loading tenants: {error.message}</div>;

  return (
    <div className="tenants-page">
      <div className="tenants-header">
        <div>
          <h1>Tenants</h1>
          <p>Manage tenant information and profiles</p>
        </div>
        <Button variant="primary" onClick={handleAddTenant}>
          Add Tenant
        </Button>
      </div>

      <div className="tenants-filters">
        <div className="filter-group">
          <input
            type="text"
            placeholder="Search tenants..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      <div className="tenants-stats">
        <div className="stat-card">
          <h3>Total Tenants</h3>
          <span className="stat-number">{tenants.length}</span>
        </div>
        <div className="stat-card">
          <h3>Active Tenants</h3>
          <span className="stat-number">
            {tenants.filter(t => t.is_active).length}
          </span>
        </div>
        <div className="stat-card">
          <h3>Active Leases</h3>
          <span className="stat-number">
            {tenants.reduce((sum, t) => sum + t.active_lease_count, 0)}
          </span>
        </div>
        <div className="stat-card">
          <h3>Total Monthly Rent</h3>
          <span className="stat-number">
            ${tenants.reduce((sum, t) => sum + parseFloat(t.monthly_rent_total), 0).toLocaleString()}
          </span>
        </div>
      </div>

      <div className="tenants-grid">
        {tenants.map((tenant) => (
          <Card
            key={tenant.id}
            title={tenant.full_name}
            subtitle={tenant.email}
            className="tenant-card"
          >
            <div className="tenant-info">
              <div className="tenant-details">
                <div className="tenant-contact">
                  <span className="tenant-phone">{tenant.phone}</span>
                  <span className="tenant-address">
                    {tenant.city}, {tenant.state}
                  </span>
                </div>
                <div className="tenant-status">
                  <span className={`status-badge ${tenant.is_active ? 'active' : 'inactive'}`}>
                    {tenant.is_active ? 'Active' : 'Inactive'}
                  </span>
                  {tenant.credit_score && (
                    <span className="credit-score">
                      Credit: {tenant.credit_score}
                    </span>
                  )}
                </div>
              </div>

              <div className="tenant-leases">
                <div className="lease-info">
                  <span className="lease-count">{tenant.active_lease_count} active lease(s)</span>
                  <span className="monthly-rent">${tenant.monthly_rent_total}/month</span>
                </div>
              </div>
            </div>

            <div className="tenant-actions">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleEditTenant(tenant)}
              >
                Edit
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => handleDeleteTenant(tenant.id)}
              >
                Delete
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Add Tenant Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={handleCloseModal}
        title="Add New Tenant"
      >
        <TenantForm onClose={handleCloseModal} />
      </Modal>

      {/* Edit Tenant Modal */}
      <Modal
        isOpen={!!editingTenant}
        onClose={handleCloseModal}
        title="Edit Tenant"
      >
        {editingTenant && (
          <TenantForm tenant={editingTenant} onClose={handleCloseModal} />
        )}
      </Modal>
    </div>
  );
};

export default TenantsPage;