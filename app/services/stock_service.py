import yfinance as yf
from yfinance import Ticker
from typing import Dict, Optional
import requests

def get_stock_info(ticker: str) -> Dict:
    """Fetch stock information from Yahoo Finance"""
    try:
        stock = Ticker(ticker)
        info = stock.info
        
        stock_info = {
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Market Cap': info.get('marketCap', 'N/A'),
            'Open': info.get('open', 'N/A'),
            'High': info.get('high', 'N/A'),
            'Low': info.get('low', 'N/A'),
            'Beta': info.get('beta', 'N/A'),
            'Trailing PE': info.get('trailingPE', 'N/A'),
            '52 Week High': info.get('52WeekHigh', 'N/A')
        }
        return stock_info
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return {
            'Sector': 'N/A',
            'Industry': 'N/A',
            'Market Cap': 'N/A',
            'Open': 'N/A',
            'High': 'N/A',
            'Low': 'N/A',
            'Beta': 'N/A',
            'Trailing PE': 'N/A',
            '52 Week High': 'N/A'
        }

def get_gics_sector(ticker: str) -> str:
    """Get GICS sector for a ticker - matches original RFL.py simple approach"""
    try:
        stock = yf.Ticker(ticker)
        return stock.info.get('sector', 'N/A')
    except:
        return 'N/A'

