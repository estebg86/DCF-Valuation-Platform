import { useState } from 'react';

export default function ValuationForm({ onSubmit, onExport, loading }) {
  const [formData, setFormData] = useState({
    ticker: '',
    projection_years: 10,
    terminal_growth_rate: 0.025,
    risk_free_rate: 0.0385,
    equity_risk_premium: 0.055,
    beta: 1.0,
    tax_rate: 0.21,
    current_price: '',
  });

  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Convert string inputs to numbers
    const processedData = {
      ...formData,
      ticker: formData.ticker.toUpperCase(),
      projection_years: parseInt(formData.projection_years),
      terminal_growth_rate: parseFloat(formData.terminal_growth_rate),
      risk_free_rate: parseFloat(formData.risk_free_rate),
      equity_risk_premium: parseFloat(formData.equity_risk_premium),
      beta: parseFloat(formData.beta),
      tax_rate: parseFloat(formData.tax_rate),
      current_price: formData.current_price ? parseFloat(formData.current_price) : null,
    };

    onSubmit(processedData);
  };

  const handleExport = () => {
    const processedData = {
      ...formData,
      ticker: formData.ticker.toUpperCase(),
      projection_years: parseInt(formData.projection_years),
      terminal_growth_rate: parseFloat(formData.terminal_growth_rate),
      risk_free_rate: parseFloat(formData.risk_free_rate),
      equity_risk_premium: parseFloat(formData.equity_risk_premium),
      beta: parseFloat(formData.beta),
      tax_rate: parseFloat(formData.tax_rate),
      current_price: formData.current_price ? parseFloat(formData.current_price) : null,
    };

    onExport(processedData);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-6">Valuation Inputs</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Ticker */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Stock Ticker
          </label>
          <input
            type="text"
            name="ticker"
            value={formData.ticker}
            onChange={handleChange}
            placeholder="e.g., AAPL"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        {/* Current Price */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Current Stock Price (Optional)
          </label>
          <input
            type="number"
            name="current_price"
            value={formData.current_price}
            onChange={handleChange}
            step="0.01"
            placeholder="e.g., 150.25"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Projection Years */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Projection Years
          </label>
          <input
            type="number"
            name="projection_years"
            value={formData.projection_years}
            onChange={handleChange}
            min="5"
            max="15"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Terminal Growth Rate */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Terminal Growth Rate (%)
          </label>
          <input
            type="number"
            name="terminal_growth_rate"
            value={formData.terminal_growth_rate * 100}
            onChange={(e) => handleChange({
              target: { name: 'terminal_growth_rate', value: e.target.value / 100 }
            })}
            step="0.1"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p className="text-xs text-gray-500 mt-1">
            Typically 2-3% for mature companies
          </p>
        </div>

        {/* Advanced Options */}
        <div>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            {showAdvanced ? '− Hide' : '+ Show'} Advanced Options
          </button>
        </div>

        {showAdvanced && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Risk-Free Rate (%)
              </label>
              <input
                type="number"
                name="risk_free_rate"
                value={formData.risk_free_rate * 100}
                onChange={(e) => handleChange({
                  target: { name: 'risk_free_rate', value: e.target.value / 100 }
                })}
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Equity Risk Premium (%)
              </label>
              <input
                type="number"
                name="equity_risk_premium"
                value={formData.equity_risk_premium * 100}
                onChange={(e) => handleChange({
                  target: { name: 'equity_risk_premium', value: e.target.value / 100 }
                })}
                step="0.1"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Beta
              </label>
              <input
                type="number"
                name="beta"
                value={formData.beta}
                onChange={handleChange}
                step="0.1"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tax Rate (%)
              </label>
              <input
                type="number"
                name="tax_rate"
                value={formData.tax_rate * 100}
                onChange={(e) => handleChange({
                  target: { name: 'tax_rate', value: e.target.value / 100 }
                })}
                step="0.1"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </>
        )}

        {/* Submit Buttons */}
        <div className="space-y-2 pt-4">
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
          >
            {loading ? 'Calculating...' : 'Calculate Valuation'}
          </button>

          <button
            type="button"
            onClick={handleExport}
            disabled={loading || !formData.ticker}
            className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
          >
            Export to Excel
          </button>
        </div>
      </form>
    </div>
  );
}
