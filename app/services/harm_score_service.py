import pandas as pd
from typing import Dict, List, Optional
import numpy as np

def calculate_portfolio_harm_scores(holdings: Optional[pd.DataFrame] = None) -> Dict:
    """Calculate portfolio harm scores using Sector Mean Score from displayed bonds"""
    
    if holdings is None or holdings.empty:
        return {
            'average_score': 0.0,
            'total_score': 0.0,
            'quartile': "N/A"
        }
    
    sector_mean_scores = []
    security_mean_scores = []
    
    for _, row in holdings.iterrows():
        sector_mean_score = row.get('Sector Mean Score', 0)
        security_mean_score = row.get('Security Mean Score', 0)
        
        try:
            score_str = str(sector_mean_score).replace(',', '').replace('$', '').strip()
            if score_str and score_str != '0' and score_str != '0.0':
                sector_mean_scores.append(float(score_str))
        except (ValueError, TypeError):
            pass
        
        try:
            security_str = str(security_mean_score).replace(',', '').replace('$', '').strip()
            if security_str and security_str != '0' and security_str != '0.0':
                security_mean_scores.append(float(security_str))
        except (ValueError, TypeError):
            pass
    
    if len(sector_mean_scores) == 0:
        return {
            'average_score': 0.0,
            'total_score': 0.0,
            'quartile': "N/A"
        }
    
    average_score = sum(sector_mean_scores) / len(sector_mean_scores)
    total_score = sum(security_mean_scores) / len(security_mean_scores) if len(security_mean_scores) > 0 else 0
    
    quartile = "N/A"
    if average_score <= 38.80:
        quartile = "Quartile 1"
    elif 38.80 < average_score <= 50.00:
        quartile = "Quartile 2"
    elif 50.00 < average_score <= 82.40:
        quartile = "Quartile 3"
    elif average_score > 82.40:
        quartile = "Quartile 4"

    return {
        'average_score': average_score,
        'total_score': total_score,
        'quartile': quartile
    }

def calculate_portfolio_harm_scores_stocks(stock_holdings: Optional[pd.DataFrame] = None) -> Dict:
    """Calculate portfolio harm scores for stocks"""
    
    if stock_holdings is None or stock_holdings.empty:
        return {
            'average_score': 0.0,
            'total_score': 0.0,
            'quartile': "N/A"
        }
    
    sector_mean_scores = []
    security_mean_scores = []
    
    for _, row in stock_holdings.iterrows():
        sector_score = row.get('Sector Mean Score', 0)
        if pd.isna(sector_score) or sector_score is None:
            sector_score = 0
        try:
            sector_score = float(sector_score)
        except (ValueError, TypeError):
            sector_score = 0
        
        security_score = row.get('Security Mean Score', 0)
        if pd.isna(security_score) or security_score is None:
            security_score = 0
        try:
            security_score = float(str(security_score).replace(',', ''))
        except (ValueError, TypeError):
            security_score = 0
        
        sector_mean_scores.append(sector_score)
        security_mean_scores.append(security_score)
    
    if len(sector_mean_scores) == 0 or len(security_mean_scores) == 0:
        return {
            'average_score': 0.0,
            'total_score': 0.0,
            'quartile': "N/A"
        }
    
    average_score = sum(sector_mean_scores) / len(sector_mean_scores)
    total_score = sum(security_mean_scores) / len(security_mean_scores)
    
    quartile = "N/A"
    if average_score <= 38.80:
        quartile = "Quartile 1"
    elif 38.80 < average_score <= 50.00:
        quartile = "Quartile 2"
    elif 50.00 < average_score <= 82.40:
        quartile = "Quartile 3"
    elif average_score > 82.40:
        quartile = "Quartile 4"
    
    return {
        'average_score': average_score,
        'total_score': total_score,
        'quartile': quartile
    }

