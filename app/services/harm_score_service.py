import pandas as pd
from typing import Dict, List, Optional
import numpy as np

def calculate_portfolio_harm_scores(holdings: Optional[pd.DataFrame] = None) -> Dict:
    """Calculate portfolio harm scores for bonds using weighted average based on portfolio allocation percentages"""
    
    if holdings is None or holdings.empty:
        return {
            'average_score': 0.0,
            'total_score': 0.0,
            'quartile': "N/A"
        }
    
    weighted_scores = []
    total_allocation = 0.0
    
    for _, row in holdings.iterrows():
        # Get portfolio allocation (weight) as percentage
        weight = row.get('weight', 0) or row.get('Weight', 0)
        if pd.isna(weight) or weight is None:
            weight = 0
        try:
            weight = float(weight)
        except (ValueError, TypeError):
            weight = 0
        
        # Get sector mean score (harm score for the asset)
        sector_score = row.get('Sector Mean Score', 0) or row.get('sector_mean_score', 0)
        if pd.isna(sector_score) or sector_score is None:
            sector_score = 0
        try:
            sector_score = float(str(sector_score).replace(',', '').replace('$', '').strip())
        except (ValueError, TypeError):
            sector_score = 0
        
        # Calculate weighted score: p_i * s_i
        if weight > 0 and sector_score > 0:
            weighted_score = weight * sector_score
            weighted_scores.append(weighted_score)
            total_allocation += weight
    
    if len(weighted_scores) == 0 or total_allocation == 0:
        return {
            'average_score': 0.0,
            'total_score': 0.0,
            'quartile': "N/A"
        }
    
    # Calculate weighted average: sum(p_i * s_i) / sum(p_i)
    # If allocations sum to 100%, the sum is the portfolio's weighted harm score
    if abs(total_allocation - 100.0) < 0.01:  # Allow small floating point differences
        # Allocations sum to 100%, so the sum is the portfolio's weighted harm score
        average_score = sum(weighted_scores)
    else:
        # Divide by total allocation if not exactly 100%
        average_score = sum(weighted_scores) / total_allocation
    
    # For total_score, sum all Security Total Scores (weighted)
    total_score = 0.0
    for _, row in holdings.iterrows():
        security_total = row.get('Security Total Score', 0) or row.get('security_total_score', 0)
        if pd.isna(security_total) or security_total is None:
            security_total = 0
        try:
            security_total = float(str(security_total).replace(',', '').replace('$', '').strip())
        except (ValueError, TypeError):
            security_total = 0
        total_score += security_total
    
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
    """Calculate portfolio harm scores for stocks using weighted average based on portfolio allocation percentages"""
    
    if stock_holdings is None or stock_holdings.empty:
        return {
            'average_score': 0.0,
            'total_score': 0.0,
            'quartile': "N/A"
        }
    
    weighted_scores = []
    total_allocation = 0.0
    
    for _, row in stock_holdings.iterrows():
        # Get portfolio allocation (weight) as percentage
        weight = row.get('weight', 0) or row.get('Weight', 0)
        if pd.isna(weight) or weight is None:
            weight = 0
        try:
            weight = float(weight)
        except (ValueError, TypeError):
            weight = 0
        
        # Get sector mean score (harm score for the asset)
        sector_score = row.get('Sector Mean Score', 0) or row.get('sector_mean_score', 0)
        if pd.isna(sector_score) or sector_score is None:
            sector_score = 0
        try:
            sector_score = float(str(sector_score).replace(',', '').replace('$', '').strip())
        except (ValueError, TypeError):
            sector_score = 0
        
        # Calculate weighted score: p_i * s_i
        if weight > 0 and sector_score > 0:
            weighted_score = weight * sector_score
            weighted_scores.append(weighted_score)
            total_allocation += weight
    
    if len(weighted_scores) == 0 or total_allocation == 0:
        return {
            'average_score': 0.0,
            'total_score': 0.0,
            'quartile': "N/A"
        }
    
    # Calculate weighted average: sum(p_i * s_i) / sum(p_i)
    # If allocations sum to 100%, the sum is the portfolio's weighted harm score
    if abs(total_allocation - 100.0) < 0.01:  # Allow small floating point differences
        # Allocations sum to 100%, so the sum is the portfolio's weighted harm score
        average_score = sum(weighted_scores)
    else:
        # Divide by total allocation if not exactly 100%
        average_score = sum(weighted_scores) / total_allocation
    
    # For total_score, sum all Security Total Scores (weighted)
    total_score = 0.0
    for _, row in stock_holdings.iterrows():
        security_total = row.get('Security Total Score', 0) or row.get('security_total_score', 0)
        if pd.isna(security_total) or security_total is None:
            security_total = 0
        try:
            security_total = float(str(security_total).replace(',', '').replace('$', '').strip())
        except (ValueError, TypeError):
            security_total = 0
        total_score += security_total
    
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

