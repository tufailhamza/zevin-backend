from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

# Stock Models - For calculating info from frontend data
class StockInfoRequest(BaseModel):
    """Request to get stock info - frontend sends this"""
    ticker: str
    weight: float  # Portfolio allocation percentage (e.g., 20.5 for 20.5%)

class BatchStockTicker(BaseModel):
    """Ticker with weight for batch request"""
    ticker: str
    weight: float  # Portfolio allocation percentage

class BatchStockInfoRequest(BaseModel):
    """Request to get stock info for multiple tickers"""
    tickers: List[BatchStockTicker]  # List of ticker symbols with weights

# Bond Models - For calculating info from frontend data
class BondInfoRequest(BaseModel):
    """Request to get bond info - frontend sends this"""
    cusip: str = Field(..., min_length=9, max_length=9)
    weight: float  # Portfolio allocation percentage (e.g., 20.5 for 20.5%)

# Portfolio Models
class PortfolioHarmScores(BaseModel):
    average_score: float
    total_score: float
    quartile: str


# Sector Models
class SectorData(BaseModel):
    sector: str
    sdh_category: str
    sdh_indicator: str
    harm_description: str
    harm_typology: str
    claim_quantification: Optional[str] = None
    total_magnitude: Optional[float] = None
    reach: Optional[float] = None
    harm_direction: Optional[float] = None
    harm_duration: Optional[float] = None
    direct_indirect_1: Optional[str] = None
    direct_indirect: Optional[str] = None
    core_peripheral: Optional[str] = None
    total_score: Optional[float] = None
    citation_1: Optional[str] = None
    citation_2: Optional[str] = None

class SankeyData(BaseModel):
    node_list: List[str]
    source: List[int]
    target: List[int]
    value: List[float]
    node_colors: List[str]
    level_colors: Dict[str, str]

class SectorInfo(BaseModel):
    sector: str
    total_score: Optional[float] = None
    mean_score: Optional[float] = None


# Report Models
class ReportRequest(BaseModel):
    sector: str
    portfolio_harm_scores: PortfolioHarmScores

# Stock Info Response (for calculation endpoint)
class StockInfoResponse(BaseModel):
    stock: str
    weight: float  # Portfolio allocation percentage
    current_price: float  # Current stock price from yfinance
    sector: str
    sector_total_score: Optional[float] = None
    sector_mean_score: Optional[float] = None
    security_total_score: Optional[float] = None
    security_mean_score: Optional[float] = None

class BatchStockInfoItem(BaseModel):
    """Stock info item for batch response"""
    ticker: str
    weight: float  # Portfolio allocation percentage
    current_price: float
    sector: str
    sector_total_score: Optional[float] = None
    sector_mean_score: Optional[float] = None
    security_total_score: Optional[float] = None
    security_mean_score: Optional[float] = None

class BatchStockInfoResponse(BaseModel):
    """Batch stock info response"""
    stocks: List[BatchStockInfoItem]

# Bond Info Response (for calculation endpoint)
class BondInfoResponse(BaseModel):
    cusip: str
    weight: float  # Portfolio allocation percentage
    industry_group: str
    sector_total_score: Optional[float] = None
    sector_mean_score: Optional[float] = None
    security_total_score: Optional[float] = None
    security_mean_score: Optional[float] = None

# Portfolio data from frontend for harm score calculation
class PortfolioStocksRequest(BaseModel):
    stocks: List[StockInfoResponse]

class PortfolioBondsRequest(BaseModel):
    bonds: List[BondInfoResponse]

# New Racial Justice Research Alert Models
class ResearchAlertItem(BaseModel):
    Sector: str
    SDH_Category: str
    SDH_Indicator: str
    Harm_Description: str
    Original_Claim_Quantification: Optional[str] = None
    New_Evidence: str
