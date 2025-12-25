'use client';

import { useEffect, useState } from 'react';

interface DataSummary {
  total_participants: number;
  survey_completed: number;
  dose_completed: number;
  both_assessments_completed: number;
  satisfaction_surveys_completed: number;
  export_endpoints: {
    csv: string;
    json: string;
  };
}

export default function AdminPage() {
  const [summary, setSummary] = useState<DataSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSummary() {
      try {
        const response = await fetch('/api/export/summary');
        if (!response.ok) throw new Error('Failed to fetch summary');
        const data = await response.json();
        setSummary(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    }
    fetchSummary();
  }, []);

  const handleDownloadCSV = () => {
    window.location.href = '/api/export/participants/csv';
  };

  const handleDownloadJSON = async () => {
    try {
      const response = await fetch('/api/export/participants/json');
      const data = await response.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `psychological_assessment_data_${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      alert('Failed to download JSON');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-red-50 text-red-700 p-6 rounded-xl max-w-md">
          <h2 className="font-bold mb-2">Error</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Admin Dashboard</h1>
          <p className="text-gray-600">Data collection summary and export tools</p>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-xl shadow-md p-5">
            <div className="text-3xl font-bold text-primary-600">{summary?.total_participants || 0}</div>
            <div className="text-sm text-gray-500">Total Participants</div>
          </div>
          <div className="bg-white rounded-xl shadow-md p-5">
            <div className="text-3xl font-bold text-blue-600">{summary?.survey_completed || 0}</div>
            <div className="text-sm text-gray-500">Survey Completed</div>
          </div>
          <div className="bg-white rounded-xl shadow-md p-5">
            <div className="text-3xl font-bold text-green-600">{summary?.dose_completed || 0}</div>
            <div className="text-sm text-gray-500">DOSE Completed</div>
          </div>
          <div className="bg-white rounded-xl shadow-md p-5">
            <div className="text-3xl font-bold text-purple-600">{summary?.both_assessments_completed || 0}</div>
            <div className="text-sm text-gray-500">Both Assessments</div>
          </div>
          <div className="bg-white rounded-xl shadow-md p-5">
            <div className="text-3xl font-bold text-orange-600">{summary?.satisfaction_surveys_completed || 0}</div>
            <div className="text-sm text-gray-500">Satisfaction Surveys</div>
          </div>
        </div>

        {/* Export Section */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Export Data</h2>
          <p className="text-gray-600 mb-6">
            Download all participant data including demographics, assessment results, and satisfaction surveys.
          </p>

          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={handleDownloadCSV}
              className="flex-1 px-6 py-4 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Download CSV
            </button>
            <button
              onClick={handleDownloadJSON}
              className="flex-1 px-6 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Download JSON
            </button>
          </div>
        </div>

        {/* API Endpoints Info */}
        <div className="bg-gray-100 rounded-xl p-6">
          <h3 className="font-semibold text-gray-900 mb-3">API Endpoints</h3>
          <div className="space-y-2 text-sm font-mono">
            <div className="bg-white px-3 py-2 rounded">
              GET /api/export/participants/csv
            </div>
            <div className="bg-white px-3 py-2 rounded">
              GET /api/export/participants/json
            </div>
            <div className="bg-white px-3 py-2 rounded">
              GET /api/export/summary
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
