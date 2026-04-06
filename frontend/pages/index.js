import { useState } from 'react';
import Head from 'next/head';
import ValuationForm from '../components/ValuationForm';
import ValuationResults from '../components/ValuationResults';
import CompanyInfo from '../components/CompanyInfo';

// Get API URL from environment variable
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [companyData, setCompanyData] = useState(null);
  const [valuationData, setValuationData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleValuation = async (formData) => {
    setLoading(true);
    setError(null);

    try {
      // Fetch valuation using environment variable for API URL
      const response = await fetch(`${API_URL}/api/valuation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Valuation request failed');
      }

      const data = await response.json();
      setValuationData(data);

      // Also fetch company details
      const companyResponse = await fetch(`${API_URL}/api/company/${formData.ticker}`);
      if (companyResponse.ok) {
        const companyInfo = await companyResponse.json();
        setCompanyData(companyInfo);
      }

    } catch (err) {
      setError(err.message || 'An error occurred. Please try again.');
      console.error('Valuation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExportExcel = async (formData) => {
    try {
      const response = await fetch(`${API_URL}/api/export/excel`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const data = await response.json();
        alert(`Excel file generated: ${data.filename}`);
      } else {
        throw new Error('Export failed');
      }
    } catch (err) {
      alert('Excel export failed. This feature may not be available in cloud deployment.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>DCF Valuation Platform</title>
        <meta name="description" content="Professional DCF valuation using SEC EDGAR data" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            DCF Valuation Platform
          </h1>
          <p className="text-gray-600">
            Automated discounted cash flow valuation using SEC EDGAR data
          </p>
          <p className="text-xs text-gray-500 mt-2">
            API: {API_URL}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Input Form */}
          <div className="lg:col-span-1">
            <ValuationForm 
              onSubmit={handleValuation}
              onExport={handleExportExcel}
              loading={loading}
            />
          </div>

          {/* Results */}
          <div className="lg:col-span-2">
            {loading && (
              <div className="bg-white rounded-lg shadow p-8 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">Calculating valuation...</p>
                <p className="text-xs text-gray-500 mt-2">Fetching SEC EDGAR data...</p>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 font-medium">Error</p>
                <p className="text-red-700 text-sm mt-1">{error}</p>
                <p className="text-xs text-gray-600 mt-2">
                  Tip: Make sure the ticker is valid and the company files with SEC
                </p>
              </div>
            )}

            {!loading && !error && companyData && (
              <CompanyInfo data={companyData} />
            )}

            {!loading && !error && valuationData && (
              <ValuationResults data={valuationData} />
            )}

            {!loading && !error && !valuationData && (
              <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <p className="mt-4">Enter a ticker symbol and click "Calculate Valuation" to get started</p>
                <p className="text-xs text-gray-400 mt-2">Try: MSFT, AAPL, GOOGL, NVDA</p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-xs text-gray-500">
          <p>Data Source: SEC EDGAR | For educational purposes only | Not investment advice</p>
        </div>
      </main>
    </div>
  );
}
