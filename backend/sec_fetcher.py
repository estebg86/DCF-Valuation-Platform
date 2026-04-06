"""
SEC EDGAR Data Fetcher
Retrieves financial data from SEC EDGAR using official APIs
"""
import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

class SECDataFetcher:
    BASE_URL = "https://data.sec.gov"
    HEADERS = {
        "User-Agent": "DCF Platform research@example.com",
        "Accept-Encoding": "gzip, deflate"
    }
    
    def __init__(self, cache_dir: str = "./data/cache"):
        self.cache_dir = cache_dir
        self.ticker_to_cik = {}
        
    def get_cik_from_ticker(self, ticker: str) -> Optional[str]:
        """Convert ticker to CIK using SEC company tickers JSON"""
        if ticker.upper() in self.ticker_to_cik:
            return self.ticker_to_cik[ticker.upper()]
        
        url = f"{self.BASE_URL}/files/company_tickers.json"
        
        try:
            response = requests.get(url, headers=self.HEADERS)
            response.raise_for_status()
            data = response.json()
            
            for entry in data.values():
                ticker_key = entry.get('ticker', '').upper()
                cik = str(entry.get('cik_str', '')).zfill(10)
                self.ticker_to_cik[ticker_key] = cik
                
            return self.ticker_to_cik.get(ticker.upper())
            
        except Exception as e:
            print(f"Error fetching ticker-CIK mapping: {e}")
            return None
    
    def get_company_submissions(self, cik: str) -> Optional[Dict]:
        """Get company submissions data"""
        url = f"{self.BASE_URL}/submissions/CIK{cik}.json"
        
        try:
            response = requests.get(url, headers=self.HEADERS)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching submissions: {e}")
            return None
    
    def get_company_facts(self, cik: str) -> Optional[Dict]:
        """Get company facts (XBRL data)"""
        url = f"{self.BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json"
        
        try:
            response = requests.get(url, headers=self.HEADERS)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching company facts: {e}")
            return None
    
    def extract_latest_filings(self, submissions: Dict, filing_type: str = "10-K", 
                              count: int = 5) -> List[Dict]:
        """Extract latest filings of specified type"""
        recent = submissions.get('filings', {}).get('recent', {})
        
        filings = []
        forms = recent.get('form', [])
        filing_dates = recent.get('filingDate', [])
        accession_numbers = recent.get('accessionNumber', [])
        primary_docs = recent.get('primaryDocument', [])
        
        for i in range(len(forms)):
            if forms[i] == filing_type:
                filings.append({
                    'form': forms[i],
                    'filing_date': filing_dates[i],
                    'accession_number': accession_numbers[i].replace('-', ''),
                    'primary_document': primary_docs[i]
                })
                
                if len(filings) >= count:
                    break
        
        return filings
    
    def extract_financial_metrics(self, company_facts: Dict) -> Dict:
        """Extract key financial metrics from company facts"""
        metrics = {}
        
        try:
            us_gaap = company_facts.get('facts', {}).get('us-gaap', {})
            
            # Revenue
            revenue_concepts = [
                'Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax',
                'SalesRevenueNet', 'RevenueFromContractWithCustomer'
            ]
            for concept in revenue_concepts:
                if concept in us_gaap:
                    metrics['Revenue'] = self._extract_annual_data(us_gaap[concept])
                    break
            
            # Net Income
            net_income_concepts = ['NetIncomeLoss', 'ProfitLoss']
            for concept in net_income_concepts:
                if concept in us_gaap:
                    metrics['NetIncome'] = self._extract_annual_data(us_gaap[concept])
                    break
            
            # Operating Income
            oi_concepts = ['OperatingIncomeLoss', 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest']
            for concept in oi_concepts:
                if concept in us_gaap:
                    metrics['OperatingIncome'] = self._extract_annual_data(us_gaap[concept])
                    break
            
            # Cost of Revenue
            cogs_concepts = ['CostOfRevenue', 'CostOfGoodsAndServicesSold']
            for concept in cogs_concepts:
                if concept in us_gaap:
                    metrics['CostOfRevenue'] = self._extract_annual_data(us_gaap[concept])
                    break
            
            # Research and Development
            if 'ResearchAndDevelopmentExpense' in us_gaap:
                metrics['RnD'] = self._extract_annual_data(us_gaap['ResearchAndDevelopmentExpense'])
            
            # SG&A
            if 'SellingGeneralAndAdministrativeExpense' in us_gaap:
                metrics['SGA'] = self._extract_annual_data(us_gaap['SellingGeneralAndAdministrativeExpense'])
            
            # Depreciation
            dep_concepts = ['DepreciationDepletionAndAmortization', 'Depreciation', 'DepreciationAndAmortization']
            for concept in dep_concepts:
                if concept in us_gaap:
                    metrics['Depreciation'] = self._extract_annual_data(us_gaap[concept])
                    break
            
            # CapEx
            capex_concepts = ['PaymentsToAcquirePropertyPlantAndEquipment', 'CapitalExpendituresIncurredButNotYetPaid']
            for concept in capex_concepts:
                if concept in us_gaap:
                    metrics['CapEx'] = self._extract_annual_data(us_gaap[concept])
                    break
            
            # Cash from Operations
            if 'NetCashProvidedByUsedInOperatingActivities' in us_gaap:
                metrics['OperatingCashFlow'] = self._extract_annual_data(us_gaap['NetCashProvidedByUsedInOperatingActivities'])
            
            # Total Assets
            if 'Assets' in us_gaap:
                metrics['TotalAssets'] = self._extract_annual_data(us_gaap['Assets'])
            
            # Current Assets
            if 'AssetsCurrent' in us_gaap:
                metrics['CurrentAssets'] = self._extract_annual_data(us_gaap['AssetsCurrent'])
            
            # Current Liabilities
            if 'LiabilitiesCurrent' in us_gaap:
                metrics['CurrentLiabilities'] = self._extract_annual_data(us_gaap['LiabilitiesCurrent'])
            
            # Long-term Debt
            debt_concepts = ['LongTermDebt', 'LongTermDebtNoncurrent']
            for concept in debt_concepts:
                if concept in us_gaap:
                    metrics['LongTermDebt'] = self._extract_annual_data(us_gaap[concept])
                    break
            
            # Shares Outstanding
            shares_concepts = ['CommonStockSharesOutstanding', 'WeightedAverageNumberOfSharesOutstandingBasic']
            for concept in shares_concepts:
                if concept in us_gaap:
                    metrics['SharesOutstanding'] = self._extract_annual_data(us_gaap[concept])
                    break
                    
        except Exception as e:
            print(f"Error extracting financial metrics: {e}")
        
        return metrics
    
    def _extract_annual_data(self, concept_data: Dict) -> Dict[str, float]:
        """Extract annual data from concept, filtering for 10-K filings"""
        annual_data = {}
        
        units = concept_data.get('units', {})
        
        # Try USD first, then shares
        for unit_type in ['USD', 'shares']:
            if unit_type in units:
                for entry in units[unit_type]:
                    # Filter for annual data (10-K filings)
                    form = entry.get('form', '')
                    if form == '10-K':
                        fiscal_year = entry.get('fy')
                        val = entry.get('val')
                        end_date = entry.get('end')
                        
                        if fiscal_year and val is not None:
                            # Use the most recent entry for each fiscal year
                            if fiscal_year not in annual_data or end_date > annual_data[fiscal_year]['end']:
                                annual_data[fiscal_year] = {
                                    'value': val,
                                    'end': end_date,
                                    'filed': entry.get('filed')
                                }
        
        # Return simplified dict with year -> value
        return {year: data['value'] for year, data in annual_data.items()}
    
    def get_company_data(self, ticker: str) -> Optional[Dict]:
        """Main method to get all company data"""
        # Get CIK
        cik = self.get_cik_from_ticker(ticker)
        if not cik:
            return None
        
        # Get submissions
        time.sleep(0.1)  # Rate limiting
        submissions = self.get_company_submissions(cik)
        if not submissions:
            return None
        
        # Get company facts
        time.sleep(0.1)  # Rate limiting
        company_facts = self.get_company_facts(cik)
        
        # Extract filings
        filings_10k = self.extract_latest_filings(submissions, "10-K", 5)
        filings_10q = self.extract_latest_filings(submissions, "10-Q", 8)
        
        # Extract metrics
        metrics = {}
        if company_facts:
            metrics = self.extract_financial_metrics(company_facts)
        
        return {
            'cik': cik,
            'ticker': ticker.upper(),
            'entity_name': submissions.get('name', ''),
            'sic': submissions.get('sic', ''),
            'sic_description': submissions.get('sicDescription', ''),
            'filings_10k': filings_10k,
            'filings_10q': filings_10q,
            'metrics': metrics,
            'fiscal_year_end': submissions.get('fiscalYearEnd', '')
        }
