import pandas as pd
from sqlalchemy import text
from app.database import engine
from typing import List, Dict, Optional, Tuple
from functools import lru_cache

def fetch_sector_scoring_data() -> pd.DataFrame:
    """Fetch sector scoring data from RHG-Sector-Scoring table"""
    try:
        print(f"Attempting to connect to database...")
        query = text("SELECT * FROM `RHG-Sector-Scoring`")
        with engine.connect() as connection:
            print(f"Database connection successful, executing query...")
            df = pd.read_sql(query, connection)
            print(f"Query successful. Fetched {len(df)} rows from RHG-Sector-Scoring")
            if not df.empty:
                print(f"Columns in result: {df.columns.tolist()}")
                print(f"Sample sectors: {df['Sector'].unique().tolist()[:10] if 'Sector' in df.columns else 'No Sector column'}")
            return df
    except Exception as e:
        print(f"ERROR fetching sector scoring data: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        # Return empty DataFrame if database connection fails
        return pd.DataFrame()

def fetch_sector_data(sector: str) -> pd.DataFrame:
    """Fetch sector data from rh_sankey2 table"""
    try:
        query = text("""
            SELECT Sector, SDH_Category, SDH_Indicator, Harm_Description, 
                  Claim_Quantification, Harm_Typology, Direct_Indirect_1, Direct_Indirect, 
                  Core_Peripheral, Total_Magnitude, Reach, 
                  Harm_Direction, Harm_Duration, Total_Score, `Citation_1`, `Citation_2`
            FROM rh_sankey2 
            WHERE Sector = :sector
        """)
        params = {"sector": sector}
        with engine.connect() as connection:
            df = pd.read_sql(query, connection, params=params)
        return df
    except Exception as e:
        # Silently return empty DataFrame if database connection fails
        return pd.DataFrame()

def fetch_sector_score_sankey(sector: str) -> Optional[float]:
    """Fetch sector total score"""
    try:
        query = text("""
            SELECT `Sector-Total-Score` FROM `RHG-Sector-Scoring`
            WHERE Sector = :sector
        """)
        params = {"sector": sector}
        with engine.connect() as connection:
            df = pd.read_sql(query, connection, params=params)
        if not df.empty:
            return float(df.iloc[0, 0])
        return None
    except Exception as e:
        print(f"Error fetching sector score: {e}")
        return None

def fetch_sector_score_sankey_minmax(sector: str) -> Optional[float]:
    """Fetch sector weighted mean score"""
    try:
        query = text("""
            SELECT `Weighted-Mean-Scores` FROM `RHG-Sector-Scoring`
            WHERE Sector = :sector
        """)
        params = {"sector": sector}
        with engine.connect() as connection:
            df = pd.read_sql(query, connection, params=params)
        if not df.empty:
            return float(df.iloc[0, 0])
        return None
    except Exception as e:
        print(f"Error fetching sector minmax score: {e}")
        return None

def prepare_sankey_data(df: pd.DataFrame, sector: str, subtract_max: bool = True, max_value: float = 15) -> Tuple[List[str], List[int], List[int], List[float]]:
    """Prepare data for Sankey diagram"""
    harm_typologies = df['Harm_Typology'].unique().tolist()
    sdh_categories = df['SDH_Category'].unique().tolist()
    sdh_indicators = df['SDH_Indicator'].unique().tolist()

    node_dict = {}
    node_list = []

    node_dict[sector] = len(node_list)
    node_list.append(sector)

    for harm_typology in harm_typologies:
        node_dict[harm_typology] = len(node_list)
        node_list.append(harm_typology)

    for sdh_category in sdh_categories:
        if sdh_category not in node_dict:
            node_dict[sdh_category] = len(node_list)
            node_list.append(sdh_category)

    for sdh_indicator in sdh_indicators:
        if sdh_indicator not in node_dict:
            node_dict[sdh_indicator] = len(node_list)
            node_list.append(sdh_indicator)

    source = []
    target = []
    value = []
    link_aggregation = {}
    
    for _, row in df.iterrows():
        harm_typology = row['Harm_Typology']
        sdh_category = row['SDH_Category']
        sdh_indicator = row['SDH_Indicator']
        raw_score = float(row['Total_Score'])
        
        if subtract_max:
            adjusted_score = max(0, max_value - raw_score)
        else:
            adjusted_score = raw_score
        
        if adjusted_score == 0:
            continue
        
        sector_index = node_dict[sector]
        harm_typology_index = node_dict[harm_typology]
        sdh_category_index = node_dict[sdh_category]
        sdh_indicator_index = node_dict[sdh_indicator]
        
        link1_key = (sector_index, harm_typology_index)
        if link1_key not in link_aggregation:
            link_aggregation[link1_key] = 0
        link_aggregation[link1_key] += adjusted_score
        
        link2_key = (harm_typology_index, sdh_category_index)
        if link2_key not in link_aggregation:
            link_aggregation[link2_key] = 0
        link_aggregation[link2_key] += adjusted_score
        
        link3_key = (sdh_category_index, sdh_indicator_index)
        if link3_key not in link_aggregation:
            link_aggregation[link3_key] = 0
        link_aggregation[link3_key] += adjusted_score

    for (src, tgt), val in link_aggregation.items():
        if val > 0:
            source.append(src)
            target.append(tgt)
            value.append(val)

    return node_list, source, target, value

def style_sankey_nodes(node_list: List[str], sector: str, df: pd.DataFrame) -> Tuple[List[str], Dict[str, str]]:
    """Style Sankey nodes with consistent level colors"""
    level_colors = {
        'sector': '#1f77b4',
        'harm_typology': '#ff7f0e',
        'sdh_category': '#2ca02c',
        'sdh_indicator': '#d62728'
    }
    
    node_colors = []
    harm_typologies = df['Harm_Typology'].unique().tolist()
    sdh_categories = df['SDH_Category'].unique().tolist()
    sdh_indicators = df['SDH_Indicator'].unique().tolist()
    
    for node in node_list:
        if node == sector:
            node_colors.append(level_colors['sector'])
        elif node in harm_typologies:
            node_colors.append(level_colors['harm_typology'])
        elif node in sdh_categories:
            node_colors.append(level_colors['sdh_category'])
        elif node in sdh_indicators:
            node_colors.append(level_colors['sdh_indicator'])
        else:
            node_colors.append('#999999')
    
    return node_colors, level_colors

