"""
DCF Valuation Model
Comprehensive discounted cash flow valuation engine
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from scipy import stats

class DCFModel:
    def __init__(self, company_data: Dict, assumptions: Dict):
        self.company_data = company_data
        self.assumptions = assumptions
        self.historical_data = self._prepare_historical_data()
        
    def _prepare_historical_data(self) -> pd.DataFrame:
        """Prepare historical financial data into DataFrame"""
        metrics = self.company_data.get('metrics', {})
        
        # Get all years from all metrics
        all_years = set()
        for metric_data in metrics.values():
            all_years.update(metric_data.keys())
        
        years = sorted([int(y) for y in all_years])
        
        # Build DataFrame
        data = {}
        for metric_name, metric_data in metrics.items():
            data[metric_name] = [metric_data.get(str(year)) for year in years]
        
        df = pd.DataFrame(data, index=years)
        df.index.name = 'FiscalYear'
        
        return df
    
    def calculate_historical_metrics(self) -> Dict:
        """Calculate key historical metrics and growth rates"""
        df = self.historical_data
        metrics = {}
        
        # Revenue growth
        if 'Revenue' in df.columns:
            revenue = df['Revenue'].dropna()
            if len(revenue) >= 2:
                growth_rates = revenue.pct_change().dropna()
                metrics['revenue_cagr_3y'] = self._calculate_cagr(revenue, periods=3)
                metrics['revenue_cagr_5y'] = self._calculate_cagr(revenue, periods=5)
                metrics['revenue_avg_growth'] = growth_rates.mean()
                metrics['revenue_std_growth'] = growth_rates.std()
        
        # Operating margin
        if 'Revenue' in df.columns and 'OperatingIncome' in df.columns:
            margins = (df['OperatingIncome'] / df['Revenue']).dropna()
            metrics['operating_margin_avg'] = margins.mean()
            metrics['operating_margin_latest'] = margins.iloc[-1] if len(margins) > 0 else None
        
        # CapEx as % of Revenue
        if 'Revenue' in df.columns and 'CapEx' in df.columns:
            capex_pct = (df['CapEx'] / df['Revenue']).dropna()
            metrics['capex_pct_revenue_avg'] = capex_pct.mean()
        
        # Depreciation as % of Revenue
        if 'Revenue' in df.columns and 'Depreciation' in df.columns:
            dep_pct = (df['Depreciation'] / df['Revenue']).dropna()
            metrics['depreciation_pct_revenue_avg'] = dep_pct.mean()
        
        # Working Capital
        if all(col in df.columns for col in ['CurrentAssets', 'CurrentLiabilities']):
            wc = df['CurrentAssets'] - df['CurrentLiabilities']
            wc_change = wc.diff().dropna()
            if 'Revenue' in df.columns:
                wc_pct = (wc_change / df['Revenue'].shift(1)).dropna()
                metrics['wc_change_pct_revenue_avg'] = wc_pct.mean()
        
        return metrics
    
    def _calculate_cagr(self, series: pd.Series, periods: int = None) -> Optional[float]:
        """Calculate CAGR for a time series"""
        series = series.dropna()
        if len(series) < 2:
            return None
        
        if periods is None or periods > len(series) - 1:
            periods = len(series) - 1
        
        start_val = series.iloc[-periods-1]
        end_val = series.iloc[-1]
        
        if start_val <= 0 or end_val <= 0:
            return None
        
        cagr = (end_val / start_val) ** (1 / periods) - 1
        return cagr
    
    def estimate_wacc(self) -> float:
        """Estimate Weighted Average Cost of Capital"""
        # Use assumptions or calculate
        if 'wacc' in self.assumptions:
            return self.assumptions['wacc']
        
        # Default WACC calculation components
        risk_free_rate = self.assumptions.get('risk_free_rate', 0.0385)
        equity_risk_premium = self.assumptions.get('equity_risk_premium', 0.055)
        beta = self.assumptions.get('beta', 1.0)
        
        # Cost of Equity (CAPM)
        cost_of_equity = risk_free_rate + beta * equity_risk_premium
        
        # Cost of Debt (simplified)
        cost_of_debt = self.assumptions.get('cost_of_debt', risk_free_rate + 0.015)
        
        # Tax rate
        tax_rate = self.assumptions.get('tax_rate', 0.21)
        
        # Debt-to-Equity ratio
        debt_to_equity = self.assumptions.get('debt_to_equity', 0.15)
        
        # WACC calculation
        equity_weight = 1 / (1 + debt_to_equity)
        debt_weight = debt_to_equity / (1 + debt_to_equity)
        
        wacc = cost_of_equity * equity_weight + cost_of_debt * (1 - tax_rate) * debt_weight
        
        return wacc
    
    def project_financials(self, years: int = 10) -> pd.DataFrame:
        """Project financial statements for future years"""
        df = self.historical_data
        
        # Get latest actual year
        latest_year = df.index.max()
        projection_years = list(range(latest_year + 1, latest_year + years + 1))
        
        # Initialize projections DataFrame
        projections = pd.DataFrame(index=projection_years)
        projections.index.name = 'FiscalYear'
        
        # Get latest values
        latest_revenue = df['Revenue'].iloc[-1] if 'Revenue' in df.columns else 0
        
        # Revenue projections
        revenue_growth = self.assumptions.get('revenue_growth', [])
        if isinstance(revenue_growth, (int, float)):
            revenue_growth = [revenue_growth] * years
        elif len(revenue_growth) < years:
            # Extend with terminal growth
            terminal_growth = self.assumptions.get('terminal_growth_rate', 0.025)
            revenue_growth = list(revenue_growth) + [terminal_growth] * (years - len(revenue_growth))
        
        revenues = []
        current_revenue = latest_revenue
        for growth_rate in revenue_growth:
            current_revenue = current_revenue * (1 + growth_rate)
            revenues.append(current_revenue)
        
        projections['Revenue'] = revenues
        
        # Operating margin
        operating_margin = self.assumptions.get('operating_margin')
        if operating_margin is None:
            # Use historical average
            hist_metrics = self.calculate_historical_metrics()
            operating_margin = hist_metrics.get('operating_margin_avg', 0.20)
        
        if isinstance(operating_margin, (int, float)):
            operating_margin = [operating_margin] * years
        
        projections['OperatingIncome'] = [
            rev * margin for rev, margin in zip(revenues, operating_margin)
        ]
        
        # Tax rate
        tax_rate = self.assumptions.get('tax_rate', 0.21)
        projections['Taxes'] = projections['OperatingIncome'] * tax_rate
        projections['NOPAT'] = projections['OperatingIncome'] - projections['Taxes']
        
        # CapEx
        capex_pct = self.assumptions.get('capex_pct_revenue')
        if capex_pct is None:
            hist_metrics = self.calculate_historical_metrics()
            capex_pct = hist_metrics.get('capex_pct_revenue_avg', 0.05)
        
        projections['CapEx'] = projections['Revenue'] * capex_pct
        
        # Depreciation
        dep_pct = self.assumptions.get('depreciation_pct_revenue')
        if dep_pct is None:
            hist_metrics = self.calculate_historical_metrics()
            dep_pct = hist_metrics.get('depreciation_pct_revenue_avg', 0.03)
        
        projections['Depreciation'] = projections['Revenue'] * dep_pct
        
        # Working Capital change
        wc_pct = self.assumptions.get('wc_change_pct_revenue')
        if wc_pct is None:
            hist_metrics = self.calculate_historical_metrics()
            wc_pct = hist_metrics.get('wc_change_pct_revenue_avg', 0.02)
        
        projections['WC_Change'] = projections['Revenue'] * wc_pct
        
        # Free Cash Flow
        projections['FCF'] = (
            projections['NOPAT'] + 
            projections['Depreciation'] - 
            projections['CapEx'] - 
            projections['WC_Change']
        )
        
        return projections
    
    def calculate_terminal_value(self, final_fcf: float, wacc: float) -> float:
        """Calculate terminal value using perpetuity growth model"""
        terminal_growth = self.assumptions.get('terminal_growth_rate', 0.025)
        
        # Terminal FCF (growing at terminal rate)
        terminal_fcf = final_fcf * (1 + terminal_growth)
        
        # Terminal value
        terminal_value = terminal_fcf / (wacc - terminal_growth)
        
        return terminal_value
    
    def calculate_dcf_valuation(self) -> Dict:
        """Main DCF valuation calculation"""
        # Project financials
        projection_years = self.assumptions.get('projection_years', 10)
        projections = self.project_financials(years=projection_years)
        
        # WACC
        wacc = self.estimate_wacc()
        
        # Discount factors
        years_from_now = list(range(1, projection_years + 1))
        discount_factors = [(1 + wacc) ** -year for year in years_from_now]
        projections['DiscountFactor'] = discount_factors
        
        # PV of FCF
        projections['PV_FCF'] = projections['FCF'] * projections['DiscountFactor']
        
        # Sum of PV of projected FCFs
        pv_projection_period = projections['PV_FCF'].sum()
        
        # Terminal value
        final_fcf = projections['FCF'].iloc[-1]
        terminal_value = self.calculate_terminal_value(final_fcf, wacc)
        
        # PV of terminal value
        final_discount_factor = discount_factors[-1]
        pv_terminal_value = terminal_value * final_discount_factor
        
        # Enterprise Value
        enterprise_value = pv_projection_period + pv_terminal_value
        
        # Equity Value
        # Adjustments
        cash = self.assumptions.get('cash', 0)
        debt = self.assumptions.get('debt', 0)
        minority_interest = self.assumptions.get('minority_interest', 0)
        
        equity_value = enterprise_value + cash - debt - minority_interest
        
        # Shares outstanding
        shares_outstanding = self.assumptions.get('shares_outstanding')
        if shares_outstanding is None:
            # Try to get from historical data
            if 'SharesOutstanding' in self.historical_data.columns:
                shares_outstanding = self.historical_data['SharesOutstanding'].iloc[-1]
        
        # Value per share
        value_per_share = None
        if shares_outstanding and shares_outstanding > 0:
            value_per_share = equity_value / shares_outstanding
        
        return {
            'projections': projections,
            'wacc': wacc,
            'pv_projection_period': pv_projection_period,
            'terminal_value': terminal_value,
            'pv_terminal_value': pv_terminal_value,
            'enterprise_value': enterprise_value,
            'equity_value': equity_value,
            'shares_outstanding': shares_outstanding,
            'value_per_share': value_per_share,
            'current_price': self.assumptions.get('current_price'),
            'upside_downside': ((value_per_share / self.assumptions.get('current_price', value_per_share)) - 1) 
                             if value_per_share and self.assumptions.get('current_price') else None
        }
    
    def sensitivity_analysis(self, wacc_range: List[float] = None, 
                           growth_range: List[float] = None) -> pd.DataFrame:
        """Perform sensitivity analysis on WACC and terminal growth rate"""
        if wacc_range is None:
            base_wacc = self.estimate_wacc()
            wacc_range = [base_wacc - 0.02, base_wacc - 0.01, base_wacc, 
                         base_wacc + 0.01, base_wacc + 0.02]
        
        if growth_range is None:
            base_growth = self.assumptions.get('terminal_growth_rate', 0.025)
            growth_range = [base_growth - 0.01, base_growth - 0.005, base_growth,
                           base_growth + 0.005, base_growth + 0.01]
        
        # Build sensitivity table
        sensitivity = pd.DataFrame(index=wacc_range, columns=growth_range)
        
        original_wacc = self.assumptions.get('wacc')
        original_growth = self.assumptions.get('terminal_growth_rate')
        
        for wacc in wacc_range:
            for growth in growth_range:
                self.assumptions['wacc'] = wacc
                self.assumptions['terminal_growth_rate'] = growth
                
                result = self.calculate_dcf_valuation()
                sensitivity.loc[wacc, growth] = result['value_per_share']
        
        # Restore original assumptions
        if original_wacc:
            self.assumptions['wacc'] = original_wacc
        else:
            self.assumptions.pop('wacc', None)
        
        if original_growth:
            self.assumptions['terminal_growth_rate'] = original_growth
        
        return sensitivity
