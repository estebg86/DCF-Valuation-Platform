"""
FastAPI Backend for DCF Valuation Platform - Cloud Deployment Version
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
import os

from sec_fetcher import SECDataFetcher
from dcf_model import DCFModel
from excel_generator import generate_excel_valuation

app = FastAPI(title="DCF Valuation Platform", version="1.0.0")

# Get allowed origins from environment variable
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
allowed_origins = [
    FRONTEND_URL,
    "http://localhost:3000",
    "http://localhost:3001",
]

# Add production frontend URLs if specified
if os.getenv("PRODUCTION_FRONTEND_URL"):
    allowed_origins.append(os.getenv("PRODUCTION_FRONTEND_URL"))

# CORS middleware - Allow all origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you might want to restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data directory
DATA_DIR = os.getenv("DATA_DIR", "./data")
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize SEC fetcher
sec_fetcher = SECDataFetcher(cache_dir=f"{DATA_DIR}/cache")

# Pydantic models
class ValuationRequest(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    projection_years: int = Field(default=10, ge=5, le=15)
    revenue_growth: Optional[List[float]] = Field(default=None, description="Revenue growth rates by year")
    operating_margin: Optional[float] = Field(default=None, ge=0, le=1)
    terminal_growth_rate: float = Field(default=0.025, ge=0, le=0.05)
    wacc: Optional[float] = Field(default=None, ge=0, le=0.30)
    risk_free_rate: float = Field(default=0.0385)
    equity_risk_premium: float = Field(default=0.055)
    beta: float = Field(default=1.0)
    tax_rate: float = Field(default=0.21, ge=0, le=0.50)
    current_price: Optional[float] = Field(default=None, gt=0)
    
class CompanyDataResponse(BaseModel):
    ticker: str
    entity_name: str
    cik: str
    sic: str
    sic_description: str
    fiscal_year_end: str
    historical_metrics: Dict[str, Any]
    latest_10k_date: Optional[str]
    
class ValuationResponse(BaseModel):
    ticker: str
    entity_name: str
    valuation_date: str
    enterprise_value: float
    equity_value: float
    value_per_share: Optional[float]
    current_price: Optional[float]
    upside_downside: Optional[float]
    wacc: float
    terminal_growth_rate: float
    projections: List[Dict]
    sensitivity_table: Optional[List[Dict]]

@app.get("/")
async def root():
    return {
        "message": "DCF Valuation Platform API - Cloud Version",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "company_data": "/api/company/{ticker}",
            "valuation": "/api/valuation",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "production")
    }

@app.get("/api/company/{ticker}", response_model=CompanyDataResponse)
async def get_company_data(ticker: str):
    """Get company data and historical financials from SEC"""
    ticker = ticker.upper()
    
    try:
        # Fetch from SEC
        company_data = sec_fetcher.get_company_data(ticker)
        
        if not company_data:
            raise HTTPException(status_code=404, detail=f"Company data not found for ticker: {ticker}")
        
        # Get latest 10-K date
        latest_10k_date = None
        if company_data.get('filings_10k'):
            latest_10k_date = company_data['filings_10k'][0].get('filing_date')
        
        return CompanyDataResponse(
            ticker=company_data['ticker'],
            entity_name=company_data['entity_name'],
            cik=company_data['cik'],
            sic=company_data['sic'],
            sic_description=company_data['sic_description'],
            fiscal_year_end=company_data['fiscal_year_end'],
            historical_metrics=company_data['metrics'],
            latest_10k_date=latest_10k_date
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching company data: {str(e)}")

@app.post("/api/valuation", response_model=ValuationResponse)
async def calculate_valuation(request: ValuationRequest):
    """Calculate DCF valuation for a company"""
    ticker = request.ticker.upper()
    
    try:
        # Fetch company data
        company_data = sec_fetcher.get_company_data(ticker)
        
        if not company_data:
            raise HTTPException(status_code=404, detail=f"Company data not found for ticker: {ticker}")
        
        # Prepare assumptions
        assumptions = {
            'projection_years': request.projection_years,
            'revenue_growth': request.revenue_growth,
            'operating_margin': request.operating_margin,
            'terminal_growth_rate': request.terminal_growth_rate,
            'wacc': request.wacc,
            'risk_free_rate': request.risk_free_rate,
            'equity_risk_premium': request.equity_risk_premium,
            'beta': request.beta,
            'tax_rate': request.tax_rate,
            'current_price': request.current_price,
        }
        
        # Initialize DCF model
        dcf = DCFModel(company_data, assumptions)
        
        # Calculate valuation
        valuation_result = dcf.calculate_dcf_valuation()
        
        # Sensitivity analysis
        sensitivity = dcf.sensitivity_analysis()
        sensitivity_list = [
            {'wacc': float(wacc), 'growth': float(growth), 'value': float(value) if value is not None else None}
            for wacc in sensitivity.index
            for growth, value in zip(sensitivity.columns, sensitivity.loc[wacc])
        ]
        
        # Convert projections to list of dicts
        projections_df = valuation_result['projections']
        projections_list = [
            {'year': int(year), **{col: float(val) if val is not None else None 
                                   for col, val in row.items()}}
            for year, row in projections_df.iterrows()
        ]
        
        return ValuationResponse(
            ticker=ticker,
            entity_name=company_data['entity_name'],
            valuation_date=datetime.now().strftime('%Y-%m-%d'),
            enterprise_value=float(valuation_result['enterprise_value']),
            equity_value=float(valuation_result['equity_value']),
            value_per_share=float(valuation_result['value_per_share']) if valuation_result['value_per_share'] else None,
            current_price=float(valuation_result['current_price']) if valuation_result['current_price'] else None,
            upside_downside=float(valuation_result['upside_downside']) if valuation_result['upside_downside'] else None,
            wacc=float(valuation_result['wacc']),
            terminal_growth_rate=float(request.terminal_growth_rate),
            projections=projections_list,
            sensitivity_table=sensitivity_list
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Valuation calculation failed: {str(e)}")

# For cloud deployment
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
