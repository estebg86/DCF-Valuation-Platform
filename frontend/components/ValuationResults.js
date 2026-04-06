import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function ValuationResults({ data }) {
  const formatCurrency = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const formatPercent = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return `${(value * 100).toFixed(2)}%`;
  };

  const formatLargeNumber = (value) => {
    if (value === null || value === undefined) return 'N/A';
    if (value >= 1e9) {
      return `$${(value / 1e9).toFixed(2)}B`;
    } else if (value >= 1e6) {
      return `$${(value / 1e6).toFixed(2)}M`;
    }
    return formatCurrency(value);
  };

  // Prepare chart data
  const chartData = data.projections.map(proj => ({
    year: proj.year,
    Revenue: proj.Revenue,
    FCF: proj.FCF,
    NOPAT: proj.NOPAT,
  }));

  // Determine upside/downside color
  const upsideColor = data.upside_downside > 0 ? 'text-green-600' : 'text-red-600';

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Valuation Summary</h2>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Enterprise Value</p>
            <p className="text-xl font-bold">{formatLargeNumber(data.enterprise_value)}</p>
          </div>
          
          <div>
            <p className="text-sm text-gray-600">Equity Value</p>
            <p className="text-xl font-bold">{formatLargeNumber(data.equity_value)}</p>
          </div>
          
          <div>
            <p className="text-sm text-gray-600">Value per Share</p>
            <p className="text-xl font-bold text-blue-600">
              {formatCurrency(data.value_per_share)}
            </p>
          </div>
          
          <div>
            <p className="text-sm text-gray-600">Current Price</p>
            <p className="text-xl font-bold">
              {data.current_price ? formatCurrency(data.current_price) : 'N/A'}
            </p>
          </div>
          
          {data.upside_downside !== null && (
            <div className="col-span-2">
              <p className="text-sm text-gray-600">Upside/(Downside)</p>
              <p className={`text-2xl font-bold ${upsideColor}`}>
                {formatPercent(data.upside_downside)}
              </p>
            </div>
          )}
        </div>

        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="font-semibold mb-3">Key Assumptions</h3>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-600">WACC:</span>
              <span className="ml-2 font-medium">{formatPercent(data.wacc)}</span>
            </div>
            <div>
              <span className="text-gray-600">Terminal Growth:</span>
              <span className="ml-2 font-medium">{formatPercent(data.terminal_growth_rate)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-bold mb-4">Financial Projections</h3>
        
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Revenue & FCF Projection</h4>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip formatter={(value) => formatLargeNumber(value)} />
              <Legend />
              <Line type="monotone" dataKey="Revenue" stroke="#3b82f6" strokeWidth={2} />
              <Line type="monotone" dataKey="FCF" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Projections Table */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-bold mb-4">Detailed Projections</h3>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Year</th>
                <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Revenue</th>
                <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">NOPAT</th>
                <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">CapEx</th>
                <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">FCF</th>
                <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">PV of FCF</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.projections.map((proj) => (
                <tr key={proj.year}>
                  <td className="px-4 py-2 text-sm font-medium text-gray-900">{proj.year}</td>
                  <td className="px-4 py-2 text-sm text-right">{formatLargeNumber(proj.Revenue)}</td>
                  <td className="px-4 py-2 text-sm text-right">{formatLargeNumber(proj.NOPAT)}</td>
                  <td className="px-4 py-2 text-sm text-right">{formatLargeNumber(proj.CapEx)}</td>
                  <td className="px-4 py-2 text-sm text-right">{formatLargeNumber(proj.FCF)}</td>
                  <td className="px-4 py-2 text-sm text-right font-medium">{formatLargeNumber(proj.PV_FCF)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Sensitivity Analysis */}
      {data.sensitivity_table && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold mb-4">Sensitivity Analysis</h3>
          <p className="text-sm text-gray-600 mb-4">
            Value per Share sensitivity to WACC and Terminal Growth Rate changes
          </p>
          
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr>
                  <th className="px-2 py-1 text-left font-medium">WACC \ Growth</th>
                  {/* Extract unique growth rates */}
                  {[...new Set(data.sensitivity_table.map(s => s.growth))]
                    .sort((a, b) => a - b)
                    .map(growth => (
                      <th key={growth} className="px-2 py-1 text-right font-medium">
                        {formatPercent(growth)}
                      </th>
                    ))}
                </tr>
              </thead>
              <tbody>
                {/* Group by WACC */}
                {[...new Set(data.sensitivity_table.map(s => s.wacc))]
                  .sort((a, b) => a - b)
                  .map(wacc => (
                    <tr key={wacc}>
                      <td className="px-2 py-1 font-medium">{formatPercent(wacc)}</td>
                      {[...new Set(data.sensitivity_table.map(s => s.growth))]
                        .sort((a, b) => a - b)
                        .map(growth => {
                          const cell = data.sensitivity_table.find(
                            s => s.wacc === wacc && s.growth === growth
                          );
                          return (
                            <td key={growth} className="px-2 py-1 text-right">
                              {cell ? formatCurrency(cell.value) : '-'}
                            </td>
                          );
                        })}
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
