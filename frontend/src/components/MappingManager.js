import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MappingManager = () => {
  const [mappings, setMappings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    jobdiva_user_id: '',
    jobdiva_user_name: '',
    goto_user_id: '',
    goto_phone_number: '',
    goto_extension: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchMappings();
  }, []);

  const fetchMappings = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/admin/mappings`);
      setMappings(response.data);
      setError('');
    } catch (err) {
      console.error('Error fetching mappings:', err);
      setError('Failed to load mappings');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/admin/mappings`, formData);
      setSuccess('Mapping created successfully!');
      setShowForm(false);
      setFormData({
        jobdiva_user_id: '',
        jobdiva_user_name: '',
        goto_user_id: '',
        goto_phone_number: '',
        goto_extension: ''
      });
      fetchMappings();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Error creating mapping:', err);
      setError(err.response?.data?.detail || 'Failed to create mapping');
    }
  };

  const handleDeactivate = async (jobdivaUserId) => {
    if (!window.confirm('Are you sure you want to deactivate this mapping?')) {
      return;
    }
    try {
      await axios.delete(`${API}/admin/mappings/${jobdivaUserId}`);
      setSuccess('Mapping deactivated successfully!');
      fetchMappings();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Error deactivating mapping:', err);
      setError('Failed to deactivate mapping');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">User Mappings</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
          data-testid="toggle-mapping-form-btn"
        >
          {showForm ? 'Cancel' : 'Add New Mapping'}
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" data-testid="error-message">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4" data-testid="success-message">
          {success}
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-gray-50 p-6 rounded-lg mb-6" data-testid="mapping-form">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                JobDiva User ID *
              </label>
              <input
                type="text"
                required
                value={formData.jobdiva_user_id}
                onChange={(e) => setFormData({...formData, jobdiva_user_id: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                data-testid="jobdiva-user-id-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                JobDiva User Name *
              </label>
              <input
                type="text"
                required
                value={formData.jobdiva_user_name}
                onChange={(e) => setFormData({...formData, jobdiva_user_name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                data-testid="jobdiva-user-name-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                GoTo User ID *
              </label>
              <input
                type="text"
                required
                value={formData.goto_user_id}
                onChange={(e) => setFormData({...formData, goto_user_id: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                data-testid="goto-user-id-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                GoTo Phone Number * (E.164 format)
              </label>
              <input
                type="text"
                required
                placeholder="+14155551234"
                value={formData.goto_phone_number}
                onChange={(e) => setFormData({...formData, goto_phone_number: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                data-testid="goto-phone-input"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                GoTo Extension (Optional)
              </label>
              <input
                type="text"
                value={formData.goto_extension}
                onChange={(e) => setFormData({...formData, goto_extension: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                data-testid="goto-extension-input"
              />
            </div>
          </div>
          <button
            type="submit"
            className="mt-4 bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition"
            data-testid="submit-mapping-btn"
          >
            Create Mapping
          </button>
        </form>
      )}

      {loading ? (
        <div className="text-center py-8">
          <p className="text-gray-600">Loading mappings...</p>
        </div>
      ) : mappings.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-600">No mappings found. Create your first mapping above.</p>
        </div>
      ) : (
        <div className="overflow-x-auto" data-testid="mappings-table">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  JobDiva User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  GoTo User ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  GoTo Phone
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Extension
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {mappings.map((mapping) => (
                <tr key={mapping.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{mapping.jobdiva_user_name}</div>
                    <div className="text-sm text-gray-500">{mapping.jobdiva_user_id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {mapping.goto_user_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {mapping.goto_phone_number}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {mapping.goto_extension || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      mapping.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {mapping.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {mapping.is_active && (
                      <button
                        onClick={() => handleDeactivate(mapping.jobdiva_user_id)}
                        className="text-red-600 hover:text-red-900"
                        data-testid={`deactivate-${mapping.jobdiva_user_id}-btn`}
                      >
                        Deactivate
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default MappingManager;
