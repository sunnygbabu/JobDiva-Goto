import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const InteractionLog = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, sms, call
  const [error, setError] = useState('');

  useEffect(() => {
    fetchLogs();
  }, [filter]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const params = filter !== 'all' ? { interaction_type: filter } : {};
      const response = await axios.get(`${API}/admin/logs`, { params });
      setLogs(response.data);
      setError('');
    } catch (err) {
      console.error('Error fetching logs:', err);
      setError('Failed to load interaction logs');
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const getStatusBadgeColor = (status) => {
    switch (status.toLowerCase()) {
      case 'sent':
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'initiated':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Interaction Logs</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg transition ${
              filter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
            data-testid="filter-all-btn"
          >
            All
          </button>
          <button
            onClick={() => setFilter('sms')}
            className={`px-4 py-2 rounded-lg transition ${
              filter === 'sms'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
            data-testid="filter-sms-btn"
          >
            SMS
          </button>
          <button
            onClick={() => setFilter('call')}
            className={`px-4 py-2 rounded-lg transition ${
              filter === 'call'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
            data-testid="filter-call-btn"
          >
            Calls
          </button>
          <button
            onClick={fetchLogs}
            className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition"
            data-testid="refresh-logs-btn"
          >
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" data-testid="error-message">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-8">
          <p className="text-gray-600">Loading logs...</p>
        </div>
      ) : logs.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-600">No interaction logs found.</p>
        </div>
      ) : (
        <div className="space-y-4" data-testid="logs-list">
          {logs.map((log) => (
            <div
              key={log.id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
              data-testid={`log-${log.id}`}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    log.interaction_type === 'sms'
                      ? 'bg-purple-100 text-purple-800'
                      : 'bg-blue-100 text-blue-800'
                  }`}>
                    {log.interaction_type.toUpperCase()}
                  </span>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    log.direction === 'outbound'
                      ? 'bg-orange-100 text-orange-800'
                      : 'bg-teal-100 text-teal-800'
                  }`}>
                    {log.direction.toUpperCase()}
                  </span>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${getStatusBadgeColor(log.status)}`}>
                    {log.status.toUpperCase()}
                  </span>
                </div>
                <span className="text-sm text-gray-500">
                  {formatTimestamp(log.timestamp)}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-2">
                <div>
                  <p className="text-sm font-medium text-gray-700">Recruiter</p>
                  <p className="text-sm text-gray-900">{log.recruiter_name}</p>
                  <p className="text-xs text-gray-500">{log.recruiter_phone}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-700">Candidate</p>
                  <p className="text-sm text-gray-900">{log.candidate_name}</p>
                  <p className="text-xs text-gray-500">{log.candidate_phone}</p>
                </div>
              </div>

              {log.message_body && (
                <div className="mt-2 p-3 bg-gray-50 rounded">
                  <p className="text-sm text-gray-700">
                    <span className="font-medium">Message:</span> {log.message_body}
                  </p>
                </div>
              )}

              {log.call_duration !== null && (
                <div className="mt-2 flex gap-4 text-sm">
                  <p className="text-gray-700">
                    <span className="font-medium">Duration:</span> {log.call_duration}s
                  </p>
                  {log.call_result && (
                    <p className="text-gray-700">
                      <span className="font-medium">Result:</span> {log.call_result}
                    </p>
                  )}
                </div>
              )}

              <div className="mt-2 flex gap-4 text-xs text-gray-500">
                <p>
                  JobDiva Note: {log.jobdiva_note_created ? (
                    <span className="text-green-600 font-medium">✓ Created</span>
                  ) : (
                    <span className="text-red-600">✗ Failed</span>
                  )}
                </p>
                {log.goto_message_id && <p>GoTo Message ID: {log.goto_message_id}</p>}
                {log.goto_call_id && <p>GoTo Call ID: {log.goto_call_id}</p>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default InteractionLog;
