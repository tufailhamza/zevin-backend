from fastapi import APIRouter, HTTPException
from app.services.portfolio_service import fetch_kataly_holdings
from typing import List, Dict, Any

router = APIRouter()

@router.get("/kataly")
async def get_kataly_holdings():
    """Get Kataly holdings from database"""
    try:
        kataly_df = fetch_kataly_holdings()
        if kataly_df.empty:
            return []
        return kataly_df.to_dict('records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Kataly holdings: {str(e)}")

