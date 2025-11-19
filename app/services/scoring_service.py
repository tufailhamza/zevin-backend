import pandas as pd
from rapidfuzz import process, fuzz
from typing import Optional

def add_scoring_columns_to_stocks(df: pd.DataFrame, sector_scoring_df: pd.DataFrame) -> pd.DataFrame:
    """Add scoring columns to stock holdings dataframe"""
    if df.empty or sector_scoring_df.empty:
        return df
    
    df_copy = df.copy()
    
    # Initialize new columns
    df_copy['Sector Total Score'] = 0.0
    df_copy['Sector Mean Score'] = 0.0
    df_copy['Security Total Score'] = 0.0
    df_copy['Security Mean Score'] = 0.0
    
    # Create a mapping dictionary from sector scoring data
    sector_mapping = {}
    for _, row in sector_scoring_df.iterrows():
        sector = row.get('Sector', '')
        sector_mapping[sector] = {
            'total_score': float(row.get('Sector-Total-Score', 0)),
            'mean_score': float(row.get('Min-Max-Norm', 0))
        }
    
    known_sectors = list(sector_mapping.keys())
    
    # Apply scoring for each row with fuzzy matching
    for idx, row in df_copy.iterrows():
        sector = row.get('Sector', 'N/A')
        units = float(row.get('Units', 0)) if pd.notna(row.get('Units', 0)) else 0
        
        # Handle common sector name variations
        sector_mappings = {
            'Consumer Cyclical': 'Consumer Discretionary',
            'Consumer Non-Cyclical': 'Consumer Staples',
            'Financial': 'Financial Services'
        }
        if sector in sector_mappings:
            sector = sector_mappings[sector]
            print(f"  Mapped sector to: {sector}")
        
        # Try exact match first
        if sector in sector_mapping:
            sector_total = sector_mapping[sector]['total_score']
            sector_mean = sector_mapping[sector]['mean_score']
            
            df_copy.at[idx, 'Sector Total Score'] = sector_total
            df_copy.at[idx, 'Sector Mean Score'] = sector_mean
            df_copy.at[idx, 'Security Total Score'] = sector_total * units
            df_copy.at[idx, 'Security Mean Score'] = sector_mean * units
            
            print(f"Matched sector '{sector}' for row {idx}: Total={sector_total}, Mean={sector_mean}, Units={units}")
        else:
            # Try fuzzy matching
            if known_sectors and sector != 'N/A':
                match_result = process.extractOne(sector, known_sectors, scorer=fuzz.token_sort_ratio)
                if match_result:
                    best_match, match_score, _ = match_result
                    if match_score >= 80:
                        sector_total = sector_mapping[best_match]['total_score']
                        sector_mean = sector_mapping[best_match]['mean_score']
                        
                        df_copy.at[idx, 'Sector Total Score'] = sector_total
                        df_copy.at[idx, 'Sector Mean Score'] = sector_mean
                        df_copy.at[idx, 'Security Total Score'] = sector_total * units
                        df_copy.at[idx, 'Security Mean Score'] = sector_mean * units
                        
                        print(f"Fuzzy matched '{row.get('Sector', 'N/A')}' -> '{best_match}' (score: {match_score}) for row {idx}: Total={sector_total}, Mean={sector_mean}, Units={units}")
                        continue
            
            print(f"WARNING: Sector '{sector}' not found in sector_mapping. Available sectors: {list(sector_mapping.keys())[:5]}...")
            print(f"  Row {idx} will have 0.0 scores")
    
    return df_copy

def add_scoring_columns_to_bonds1(df: pd.DataFrame, sector_scoring_df: pd.DataFrame) -> pd.DataFrame:
    """Add harm scoring columns to bond holdings dataframe using fuzzy-matched sector names."""
    
    if df.empty:
        return df
    
    df_copy = df.copy()
    
    # Initialize scoring columns (always initialize, even if sector_scoring_df is empty)
    df_copy['Sector Total Score'] = 0.0
    df_copy['Sector Mean Score'] = 0.0
    df_copy['Security Total Score'] = 0.0
    df_copy['Security Mean Score'] = 0.0
    
    if sector_scoring_df.empty:
        return df_copy

    # Build a mapping of known sectors to their scores
    sector_mapping = {}
    for _, row in sector_scoring_df.iterrows():
        sector = row.get('Sector', '')
        if pd.notna(sector):
            sector_mapping[sector] = {
                'total_score': float(row.get('Sector-Total-Score', 0)),
                'mean_score': float(row.get('Min-Max-Norm', 0))
            }

    known_sectors = list(sector_mapping.keys())

    # Apply scoring based on fuzzy-matched sectors
    for idx, row in df_copy.iterrows():
        input_sector = row.get('Industry Group', 'N/A')
        quantity = float(row.get('Units', 0)) if pd.notna(row.get('Units', 0)) else 0

        if input_sector == 'Financial':
            input_sector = 'Financial Services'
        
        if not known_sectors:
            continue
        
        match_result = process.extractOne(input_sector, known_sectors, scorer=fuzz.token_sort_ratio)
        
        if match_result is None:
            continue
        
        best_match, match_score, _ = match_result

        if match_score >= 80:
            sector_total = sector_mapping[best_match]['total_score']
            sector_mean = sector_mapping[best_match]['mean_score']

            df_copy.at[idx, 'Sector Total Score'] = sector_total
            df_copy.at[idx, 'Sector Mean Score'] = sector_mean
            df_copy.at[idx, 'Security Total Score'] = sector_total * quantity
            df_copy.at[idx, 'Security Mean Score'] = sector_mean * quantity

    return df_copy

