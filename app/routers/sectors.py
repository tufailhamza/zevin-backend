from fastapi import APIRouter, HTTPException
from app.models import SectorData, SankeyData, SectorInfo
from app.services.sector_service import (
    fetch_sector_data, fetch_sector_score_sankey, fetch_sector_score_sankey_minmax,
    prepare_sankey_data, style_sankey_nodes
)
from typing import List, Optional
import pandas as pd

router = APIRouter()

@router.get("/list", response_model=List[str])
async def get_available_sectors():
    """Get list of all available sectors from database"""
    try:
        from app.services.sector_service import fetch_sector_scoring_data
        import pandas as pd
        
        sector_scoring_df = fetch_sector_scoring_data()
        print(f"\n=== Fetching available sectors ===")
        print(f"Sector scoring dataframe rows: {len(sector_scoring_df)}")
        
        sectors = set()
        
        # Get sectors from scoring data
        if not sector_scoring_df.empty and 'Sector' in sector_scoring_df.columns:
            db_sectors = sector_scoring_df['Sector'].unique().tolist()
            print(f"Sectors from database: {db_sectors}")
            for sector in db_sectors:
                if sector and pd.notna(sector):
                    sectors.add(sector)
        
        # Also get sectors from Kataly holdings if available
        from app.services.portfolio_service import fetch_kataly_holdings
        kataly_holdings = fetch_kataly_holdings()
        if not kataly_holdings.empty and 'Sector' in kataly_holdings.columns:
            kataly_sectors = kataly_holdings['Sector'].unique().tolist()
            print(f"Sectors from Kataly holdings: {kataly_sectors}")
            for sector in kataly_sectors:
                if sector and sector != 'N/A' and pd.notna(sector):
                    sectors.add(sector)
        
        final_sectors = sorted(list(sectors))
        print(f"Final sectors list ({len(final_sectors)} sectors): {final_sectors}")
        print("=" * 50)
        
        return final_sectors
    except Exception as e:
        print(f"Error fetching sectors: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching sectors: {str(e)}")

@router.get("/{sector}/data", response_model=List[SectorData])
async def get_sector_data(sector: str):
    """Get detailed sector data (Sector Equity Profile)"""
    try:
        df = fetch_sector_data(sector)
        if df.empty:
            return []
        
        return [SectorData(
            sector=row.get('Sector', ''),
            sdh_category=row.get('SDH_Category', ''),
            sdh_indicator=row.get('SDH_Indicator', ''),
            harm_description=row.get('Harm_Description', ''),
            harm_typology=row.get('Harm_Typology', ''),
            claim_quantification=row.get('Claim_Quantification'),
            total_magnitude=row.get('Total_Magnitude'),
            reach=row.get('Reach'),
            harm_direction=row.get('Harm_Direction'),
            harm_duration=row.get('Harm_Duration'),
            direct_indirect_1=row.get('Direct_Indirect_1'),
            direct_indirect=row.get('Direct_Indirect'),
            core_peripheral=row.get('Core_Peripheral'),
            total_score=row.get('Total_Score'),
            citation_1=row.get('Citation_1'),
            citation_2=row.get('Citation_2')
        ) for _, row in df.iterrows()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sector data: {str(e)}")

@router.get("/{sector}/profile", response_model=List[dict])
async def get_sector_profile(sector: str):
    """Get formatted Sector Equity Profile (same as /data but with formatted column names)"""
    try:
        print(f"\n=== Fetching sector profile for: {sector} ===")
        df = fetch_sector_data(sector)
        print(f"Fetched {len(df)} rows from database")
        
        if df.empty:
            print("WARNING: DataFrame is empty, returning empty list")
            return []
        
        print(f"DataFrame columns: {df.columns.tolist()}")
        
        # Select and rename columns to match the original display format
        profile_df = df[['SDH_Indicator', 'SDH_Category', 'Harm_Description', 'Harm_Typology', 
                        'Claim_Quantification', 'Total_Magnitude', 'Reach', 'Harm_Direction', 
                        'Harm_Duration', 'Total_Score', 'Direct_Indirect', 'Direct_Indirect_1',
                        'Core_Peripheral', 'Citation_1', 'Citation_2']].copy()
        
        print(f"Profile DataFrame shape: {profile_df.shape}")
        
        profile_df = profile_df.rename(columns={
            'SDH_Indicator': 'SDH Indicator',
            'SDH_Category': 'SDH Category',
            'Harm_Description': 'Equity Description',
            'Harm_Typology': 'Equity Typology',
            'Claim_Quantification': 'Claim Quantification',
            'Total_Magnitude': 'Total Magnitude',
            'Harm_Direction': 'Equity Direction',
            'Harm_Duration': 'Equity Duration',
            'Total_Score': 'Total Score'
        })
        
        # Format numeric columns
        numeric_cols = ['Total Magnitude', 'Reach', 'Equity Direction', 'Equity Duration', 'Total Score']
        for col in numeric_cols:
            if col in profile_df.columns:
                profile_df[col] = profile_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "0.00")
        
        result = profile_df.to_dict('records')
        print(f"Converted to {len(result)} records")
        print(f"First record keys: {list(result[0].keys()) if result else 'No records'}")
        if result:
            print(f"First record sample: {list(result[0].items())[:3]}...")
        print("=" * 50)
        
        return result
    except Exception as e:
        print(f"ERROR in get_sector_profile: {type(e).__name__}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error fetching sector profile: {str(e)}")

@router.get("/{sector}/sankey", response_model=SankeyData)
async def get_sankey_data(sector: str, subtract_max: bool = True, max_value: float = 15):
    """Get Sankey diagram data for a sector"""
    try:
        df = fetch_sector_data(sector)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for sector: {sector}")
        
        node_list, source, target, value = prepare_sankey_data(df, sector, subtract_max, max_value)
        node_colors, level_colors = style_sankey_nodes(node_list, sector, df)
        
        return SankeyData(
            node_list=node_list,
            source=source,
            target=target,
            value=value,
            node_colors=node_colors,
            level_colors=level_colors
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Sankey data: {str(e)}")

@router.get("/{sector}/info", response_model=SectorInfo)
async def get_sector_info(sector: str):
    """Get sector scoring information"""
    try:
        total_score = fetch_sector_score_sankey(sector)
        mean_score = fetch_sector_score_sankey_minmax(sector)
        
        return SectorInfo(
            sector=sector,
            total_score=total_score,
            mean_score=mean_score
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sector info: {str(e)}")

