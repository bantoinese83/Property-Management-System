import React from 'react';
import { useForm } from '../../hooks/useForm';
import { API_ENDPOINTS } from '../../api/endpoints';
import { Tenant } from '../../types/models';
import Button from '../common/Button';
import Input from '../common/Input';
import client from '../../api/client';

interface TenantFormProps {
  tenant?: Tenant;
  onClose: () => void;
}

const TenantForm: React.FC<TenantFormProps> = ({ tenant, onClose }) => {
  const isEditing = !!tenant;

  const { values, errors, loading, handleChange, handleSubmit, setValue } = useForm<Tenant>({
    initialValues: tenant || {
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      date_of_birth: undefined,
      address: '',
      city: '',
      state: '',
      zip_code: '',
      emergency_contact_name: '',
      emergency_contact_phone: '',
      emergency_contact_relationship: '',
      employer_name: '',
      employer_phone: '',
      annual_income: undefined,
      previous_landlord_name: '',
      previous_landlord_phone: '',
      is_active: true,
      credit_score: undefined,
    },
    onSubmit: async (formData) => {
      try {
        const url = isEditing
          ? API_ENDPOINTS.TENANTS.DETAIL(tenant!.id)
          : API_ENDPOINTS.TENANTS.LIST;

        const method = isEditing ? 'PUT' : 'POST';

        await client({
          method,
          url,
          data: formData,
        });

        onClose();
      } catch (error: any) {
        throw new Error(error.response?.data?.detail || 'Failed to save tenant');
      }
    },
  });

  return (
    <form onSubmit={handleSubmit} className="tenant-form">
      <div className="form-grid">
        {/* Basic Information */}
        <div className="form-section">
          <h3>Basic Information</h3>

          <div className="form-row">
            <Input
              label="First Name"
              name="first_name"
              value={values.first_name}
              onChange={handleChange}
              error={errors.first_name}
              required
              fullWidth
            />

            <Input
              label="Last Name"
              name="last_name"
              value={values.last_name}
              onChange={handleChange}
              error={errors.last_name}
              required
              fullWidth
            />
          </div>

          <div className="form-row">
            <Input
              label="Email"
              name="email"
              type="email"
              value={values.email}
              onChange={handleChange}
              error={errors.email}
              required
              fullWidth
            />

            <Input
              label="Phone"
              name="phone"
              type="tel"
              value={values.phone}
              onChange={handleChange}
              fullWidth
            />
          </div>

          <Input
            label="Date of Birth"
            name="date_of_birth"
            type="date"
            value={values.date_of_birth || ''}
            onChange={handleChange}
            fullWidth
          />
        </div>

        {/* Address Information */}
        <div className="form-section">
          <h3>Address</h3>

          <Input
            label="Street Address"
            name="address"
            value={values.address}
            onChange={handleChange}
            fullWidth
          />

          <div className="form-row">
            <Input
              label="City"
              name="city"
              value={values.city}
              onChange={handleChange}
              fullWidth
            />

            <Input
              label="State"
              name="state"
              value={values.state}
              onChange={handleChange}
              fullWidth
            />
          </div>

          <Input
            label="ZIP Code"
            name="zip_code"
            value={values.zip_code}
            onChange={handleChange}
            fullWidth
          />
        </div>

        {/* Emergency Contact */}
        <div className="form-section">
          <h3>Emergency Contact</h3>

          <Input
            label="Contact Name"
            name="emergency_contact_name"
            value={values.emergency_contact_name}
            onChange={handleChange}
            fullWidth
          />

          <div className="form-row">
            <Input
              label="Contact Phone"
              name="emergency_contact_phone"
              type="tel"
              value={values.emergency_contact_phone}
              onChange={handleChange}
              fullWidth
            />

            <Input
              label="Relationship"
              name="emergency_contact_relationship"
              value={values.emergency_contact_relationship}
              onChange={handleChange}
              fullWidth
            />
          </div>
        </div>

        {/* Employment Information */}
        <div className="form-section">
          <h3>Employment Information</h3>

          <Input
            label="Employer Name"
            name="employer_name"
            value={values.employer_name}
            onChange={handleChange}
            fullWidth
          />

          <div className="form-row">
            <Input
              label="Employer Phone"
              name="employer_phone"
              type="tel"
              value={values.employer_phone}
              onChange={handleChange}
              fullWidth
            />

            <Input
              label="Annual Income"
              name="annual_income"
              type="number"
              value={values.annual_income || ''}
              onChange={handleChange}
              min="0"
              fullWidth
            />
          </div>
        </div>

        {/* References */}
        <div className="form-section">
          <h3>Previous Landlord Reference</h3>

          <div className="form-row">
            <Input
              label="Previous Landlord Name"
              name="previous_landlord_name"
              value={values.previous_landlord_name}
              onChange={handleChange}
              fullWidth
            />

            <Input
              label="Previous Landlord Phone"
              name="previous_landlord_phone"
              type="tel"
              value={values.previous_landlord_phone}
              onChange={handleChange}
              fullWidth
            />
          </div>

          <Input
            label="Credit Score"
            name="credit_score"
            type="number"
            value={values.credit_score || ''}
            onChange={handleChange}
            min="300"
            max="850"
            fullWidth
          />
        </div>

        {/* Status */}
        <div className="form-section">
          <h3>Status</h3>

          <div className="form-checkboxes">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="is_active"
                checked={values.is_active}
                onChange={(e) => setValue('is_active', e.target.checked)}
              />
              Tenant is active
            </label>
          </div>
        </div>
      </div>

      {errors.submit && (
        <div className="form-error">
          {errors.submit}
        </div>
      )}

      <div className="form-actions">
        <Button type="button" variant="ghost" onClick={onClose}>
          Cancel
        </Button>
        <Button type="submit" variant="primary" loading={loading}>
          {isEditing ? 'Update Tenant' : 'Add Tenant'}
        </Button>
      </div>
    </form>
  );
};

export default TenantForm;