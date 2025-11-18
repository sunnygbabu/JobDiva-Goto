import React from 'react';
import MappingManager from '../components/MappingManager';
import InteractionLog from '../components/InteractionLog';

const AdminPage = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-gray-900" data-testid="admin-page-title">
            JobDiva-GoTo Bridge Admin
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage user mappings and view interaction history
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          <section data-testid="mapping-manager-section">
            <MappingManager />
          </section>

          <section data-testid="interaction-log-section">
            <InteractionLog />
          </section>
        </div>
      </main>

      <footer className="bg-white mt-12 border-t">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            JobDiva-GoTo Bridge Service v1.0.0
          </p>
          <p className="text-center text-xs text-gray-400 mt-2">
            <span className="inline-block bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
              MOCKED APIs - Replace with real credentials when ready
            </span>
          </p>
        </div>
      </footer>
    </div>
  );
};

export default AdminPage;
