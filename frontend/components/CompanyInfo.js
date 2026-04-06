export default function CompanyInfo({ data }) {
  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4">{data.entity_name}</h2>
      
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-gray-600">Ticker</p>
          <p className="font-medium">{data.ticker}</p>
        </div>
        
        <div>
          <p className="text-gray-600">CIK</p>
          <p className="font-medium">{data.cik}</p>
        </div>
        
        <div>
          <p className="text-gray-600">Industry</p>
          <p className="font-medium">{data.sic_description || 'N/A'}</p>
        </div>
        
        <div>
          <p className="text-gray-600">Fiscal Year End</p>
          <p className="font-medium">{data.fiscal_year_end || 'N/A'}</p>
        </div>
        
        <div className="col-span-2">
          <p className="text-gray-600">Latest 10-K Filing</p>
          <p className="font-medium">{data.latest_10k_date || 'N/A'}</p>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500">
          Data Source: SEC EDGAR | This valuation is for educational purposes only
        </p>
      </div>
    </div>
  );
}
