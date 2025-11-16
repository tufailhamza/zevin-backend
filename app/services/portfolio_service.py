import pandas as pd
import yfinance as yf
from yfinance import Ticker
import requests
import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Optional
from app.services.bond_service import get_bond_info, calculate_returns
from app.services.stock_service import get_stock_info, get_gics_sector
from app.services.scoring_service import add_scoring_columns_to_stocks, add_scoring_columns_to_bonds1
from app.database import engine
from sqlalchemy import text

# Portfolio storage removed - frontend will manage this

company_tickers = {
    "AMERICAN EXPRESS CO": "AXP",
    "ANALOG DEVICES INC": "ADI",
    "ASTRAZENECA PLC": "AZN",
    "BIOGEN INC": "BIIB",
    "BRISTOL-MYERS SQUIBB CO": "BMY",
    "THE CIGNA GROUP": "CI",
    "CUMMINS INC": "CMI",
    "DISNEY WALT CO": "DIS",
    "ECOLAB INC": "ECL",
    "ENTERGY CORP": "ETR",
    "FEDERAL HOME LOAN BANKS": "Agency Bonds", 
    "FEDERAL FARM CREDIT BANKS": "Agency Bonds", 
    "GILEAD SCIENCES INC": "GILD",
    "HUMANA INC": "HUM",
    "JOHNSON & JOHNSON": "JNJ",
    "LABORATORY CORP AMERICA HOLDIN": "LH",
    "MASTERCARD INCORPORATED": "MA",
    "MCKESSON CORP": "MCK",
    "UNION PACIFIC CORP": "UNP",
    "UNITED STATES TREAS BILLS": "Agency Bonds",  
    "UNITED STATES TREAS NOTES": "Agency Bonds",  
    "UNITEDHEALTH GROUP INC": "UNH",
    "VISA INC": "V",
    "VODAFONE GROUP PLC": "VOD"
}

def get_current_price_direct(ticker: str) -> Optional[float]:
    """Get current price using direct Yahoo Finance API call"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        result = r.json()
        try:
            price = result['chart']['result'][0]['meta']['regularMarketPrice']
            return price
        except (KeyError, IndexError):
            return None
    except Exception:
        return None

def get_historical_price_direct(ticker: str, date: datetime.date) -> Optional[float]:
    """Get historical price for a specific date using direct API call"""
    try:
        # Convert date to timestamp
        from datetime import datetime as dt
        timestamp = int(dt.combine(date, dt.min.time()).timestamp())
        
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        params = {
            'period1': timestamp,
            'period2': timestamp + 86400,  # Add 1 day
            'interval': '1d'
        }
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, params=params, timeout=10)
        result = r.json()
        try:
            # Get the close price from the first available data point
            closes = result['chart']['result'][0]['indicators']['quote'][0]['close']
            # Filter out None values and get first valid close
            valid_closes = [c for c in closes if c is not None]
            if valid_closes:
                return valid_closes[0]
            return None
        except (KeyError, IndexError):
            return None
    except Exception:
        return None

def calculate_stock_info(ticker: str, units: int, purchase_date: datetime.date, purchase_price: Optional[float] = None):
    """Calculate stock information and returns data - uses direct Yahoo Finance API"""
    try:
        # Get current price using direct API call (works better than yfinance)
        current_price_stock = get_current_price_direct(ticker)
        
        if current_price_stock is None:
            # Fallback to yfinance if direct API fails
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1d")
                if not hist.empty:
                    current_price_stock = float(hist.iloc[-1]['Close'])
                else:
                    raise ValueError(f"Unable to fetch current price for {ticker}")
            except Exception:
                raise ValueError(f"Unable to fetch current price for {ticker}. Please verify the ticker symbol.")
        
        # Get purchase price
        if purchase_price is None:
            # Try direct API first
            purchase_price = get_historical_price_direct(ticker, purchase_date)
            
            if purchase_price is None:
                # Fallback to yfinance
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(start=purchase_date)
                    if hist.empty:
                        raise ValueError("No data available for the selected date. Please choose a valid trading day.")
                    purchase_price = float(hist.iloc[0]['Close'])
                except Exception as e:
                    raise ValueError(f"No data available for the selected date. Please choose a valid trading day. Error: {str(e)}")
        
        # Calculate values
        initial_investment_stock = purchase_price * units
        current_value = current_price_stock * units
        gain_loss = current_value - initial_investment_stock
        gain_loss_percentage = (gain_loss / initial_investment_stock) * 100 if initial_investment_stock > 0 else 0

        # Get sector
        gics_sector = get_gics_sector(ticker)
        
        stock_data = {
            'Stock': ticker,
            'Units': units,
            'Purchase Date': purchase_date,
            'Purchase Price ($)': purchase_price,
            'Current Price ($)': current_price_stock,
            'Initial Investment ($)': initial_investment_stock,
            'Current Value ($)': current_value,
            'Gain/Loss ($)': gain_loss,
            'Gain/Loss (%)': gain_loss_percentage,
            'Portfolio Allocation': "0.00%",
            'Sector': gics_sector
        }
        
        return stock_data
    except ValueError:
        # Re-raise ValueError as-is (these are user-friendly messages)
        raise
    except Exception as e:
        raise ValueError(f"An error occurred: {str(e)}")

def calculate_bond_info(cusip: str, units: int, purchase_price: float, purchase_date: datetime.date):
    """Calculate bond information and returns data"""
    if len(cusip) != 9:
        raise ValueError("CUSIP must be 9 characters")
    
    bond_info = get_bond_info(cusip)
    if not bond_info:
        raise ValueError(f"Could not fetch bond information for CUSIP {cusip}")
    
    bond_info['CUSIP'] = cusip
    bond_info['Units'] = units
    bond_info['Purchase Price'] = purchase_price
    bond_info['Purchase Date'] = purchase_date
    
    # Calculate returns
    returns = calculate_returns(bond_info)
    bond_info.update(returns)
    
    return bond_info

def calculate_portfolio_allocation(stocks: List[Dict]) -> List[Dict]:
    """Calculate portfolio allocation percentages for stocks"""
    if not stocks:
        return stocks
    
    total_value = sum(s.get('Current Value ($)', 0) for s in stocks)
    if total_value > 0:
        for stock in stocks:
            allocation = (stock.get('Current Value ($)', 0) / total_value) * 100
            stock['Portfolio Allocation'] = f"{allocation:.2f}%"
    
    return stocks

def add_scoring_to_stocks(stocks: List[Dict], sector_scoring_df: Optional[pd.DataFrame] = None) -> List[Dict]:
    """Add scoring columns to stocks"""
    if not stocks:
        return stocks
    
    stocks_df = pd.DataFrame(stocks)
    
    if sector_scoring_df is not None and not sector_scoring_df.empty:
        stocks_df = add_scoring_columns_to_stocks(stocks_df, sector_scoring_df)
    
    return stocks_df.to_dict('records')

def add_scoring_to_bonds(bonds: List[Dict], sector_scoring_df: Optional[pd.DataFrame] = None) -> List[Dict]:
    """Add scoring columns to bonds"""
    if not bonds:
        return bonds
    
    bonds_df = pd.DataFrame(bonds)
    
    if sector_scoring_df is not None and not sector_scoring_df.empty:
        # Select relevant columns for scoring
        if not bonds_df.empty:
            bonds_df = add_scoring_columns_to_bonds1(
                bonds_df[['CUSIP', 'Industry Group', 'Issuer', 'Units', 'Current Price', 
                         'Purchase Price', 'Coupon', 'Price Return', 'Income Return', 'Total Return']],
                sector_scoring_df
            )
    
    return bonds_df.to_dict('records')

def fetch_kataly_holdings():
    """Fetch Kataly holdings from database"""
    try:
        query = text("SELECT * FROM `Kataly-Holdings`")
        with engine.connect() as connection:
            df = pd.read_sql(query, connection)
        return df
    except Exception as e:
        # Silently return empty DataFrame if database connection fails
        # This allows the app to work even when database is unavailable
        return pd.DataFrame()

