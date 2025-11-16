from fastapi import APIRouter, HTTPException
from app.models import (
    StockInfoRequest, StockInfoResponse, BondInfoRequest, BondInfoResponse,
    PortfolioStocksRequest, PortfolioBondsRequest, PortfolioHarmScores
)
from app.services.portfolio_service import (
    calculate_stock_info, calculate_bond_info
)
from app.services.scoring_service import add_scoring_columns_to_stocks, add_scoring_columns_to_bonds1
from app.services.sector_service import fetch_sector_scoring_data
from app.services.harm_score_service import calculate_portfolio_harm_scores, calculate_portfolio_harm_scores_stocks
import pandas as pd

router = APIRouter()

@router.post("/stocks/info", response_model=StockInfoResponse)
async def get_stock_info(stock_request: StockInfoRequest):
    """Calculate stock information and scores from ticker and purchase data"""
    try:
        stock_data = calculate_stock_info(
            ticker=stock_request.ticker,
            units=stock_request.units,
            purchase_date=stock_request.purchase_date,
            purchase_price=stock_request.purchase_price
        )
        
        # Get sector scoring data and add scores
        sector_scoring_df = fetch_sector_scoring_data()
        if not sector_scoring_df.empty:
            stocks_df = pd.DataFrame([stock_data])
            stocks_df = add_scoring_columns_to_stocks(stocks_df, sector_scoring_df)
            stock_data = stocks_df.iloc[0].to_dict()
        else:
            # If no sector scoring data, set defaults
            stock_data['Sector Total Score'] = 0.0
            stock_data['Sector Mean Score'] = 0.0
            stock_data['Security Total Score'] = 0.0
            stock_data['Security Mean Score'] = 0.0
        
        # Debug: Print scoring values
        print(f"Scoring values for {stock_data.get('Stock')}:")
        print(f"  Sector: {stock_data.get('Sector')}")
        print(f"  Sector Total Score: {stock_data.get('Sector Total Score')}")
        print(f"  Sector Mean Score: {stock_data.get('Sector Mean Score')}")
        print(f"  Security Total Score: {stock_data.get('Security Total Score')}")
        print(f"  Security Mean Score: {stock_data.get('Security Mean Score')}")
        
        return StockInfoResponse(
            stock=stock_data['Stock'],
            units=stock_data['Units'],
            purchase_date=stock_data['Purchase Date'],
            purchase_price=stock_data['Purchase Price ($)'],
            current_price=stock_data['Current Price ($)'],
            initial_investment=stock_data['Initial Investment ($)'],
            current_value=stock_data['Current Value ($)'],
            gain_loss=stock_data['Gain/Loss ($)'],
            gain_loss_percentage=stock_data['Gain/Loss (%)'],
            sector=stock_data['Sector'],
            sector_total_score=stock_data.get('Sector Total Score', 0.0),
            sector_mean_score=stock_data.get('Sector Mean Score', 0.0),
            security_total_score=stock_data.get('Security Total Score', 0.0),
            security_mean_score=stock_data.get('Security Mean Score', 0.0)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating stock info: {str(e)}")

@router.post("/bonds/info", response_model=BondInfoResponse)
async def get_bond_info(bond_request: BondInfoRequest):
    """Calculate bond information and scores from CUSIP and purchase data"""
    try:
        bond_data = calculate_bond_info(
            cusip=bond_request.cusip,
            units=bond_request.units,
            purchase_price=bond_request.purchase_price,
            purchase_date=bond_request.purchase_date
        )
        
        # Get sector scoring data and add scores
        sector_scoring_df = fetch_sector_scoring_data()
        if not sector_scoring_df.empty:
            bonds_df = pd.DataFrame([bond_data])
            bonds_df = add_scoring_columns_to_bonds1(
                bonds_df[['CUSIP', 'Industry Group', 'Issuer', 'Units', 'Current Price',
                         'Purchase Price', 'Coupon', 'Price Return', 'Income Return', 'Total Return']],
                sector_scoring_df
            )
            bond_data = bonds_df.iloc[0].to_dict()
        
        return BondInfoResponse(
            cusip=bond_data['CUSIP'],
            name=bond_data.get('Name', 'Unknown'),
            industry_group=bond_data.get('Industry Group', 'Unknown'),
            issuer=bond_data.get('Issuer', 'Unknown'),
            units=bond_data['Units'],
            purchase_price=bond_data['Purchase Price'],
            purchase_date=bond_data['Purchase Date'],
            current_price=bond_data.get('Current Price', 0),
            coupon=bond_data.get('Coupon', 0),
            maturity_date=bond_data.get('Maturity Date'),
            ytm=bond_data.get('YTM', 0),
            market_value=bond_data.get('Market Value'),
            total_cost=bond_data.get('Total Cost'),
            price_return=bond_data.get('Price Return'),
            income_return=bond_data.get('Income Return'),
            total_return=bond_data.get('Total Return'),
            sector_total_score=bond_data.get('Sector Total Score'),
            sector_mean_score=bond_data.get('Sector Mean Score'),
            security_total_score=bond_data.get('Security Total Score'),
            security_mean_score=bond_data.get('Security Mean Score')
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating bond info: {str(e)}")

@router.post("/harm-scores/stocks", response_model=PortfolioHarmScores)
async def calculate_stock_harm_scores(portfolio_request: PortfolioStocksRequest):
    """Calculate portfolio harm scores for stocks (accepts stock data from frontend)"""
    try:
        print(f"\n=== Calculating Stock Portfolio Harm Scores ===")
        print(f"Received {len(portfolio_request.stocks)} stocks")
        
        stocks = [stock.model_dump() for stock in portfolio_request.stocks]
        stocks_df = pd.DataFrame(stocks)
        
        print(f"DataFrame shape: {stocks_df.shape}")
        print(f"DataFrame columns: {stocks_df.columns.tolist()}")
        
        # Print each stock's data
        for idx, row in stocks_df.iterrows():
            print(f"\nStock {idx + 1}:")
            print(f"  Stock: {row.get('stock', 'N/A')}")
            print(f"  Units: {row.get('units', 'N/A')}")
            print(f"  Sector: {row.get('sector', 'N/A')}")
            print(f"  Sector Total Score: {row.get('sector_total_score', 'N/A')}")
            print(f"  Sector Mean Score: {row.get('sector_mean_score', 'N/A')}")
            print(f"  Security Total Score: {row.get('security_total_score', 'N/A')}")
            print(f"  Security Mean Score: {row.get('security_mean_score', 'N/A')}")
        
        # Check if scores are present (handle both snake_case and space-separated column names)
        has_scores = ('Sector Mean Score' in stocks_df.columns or 
                     'sector_mean_score' in stocks_df.columns or
                     'Sector_Mean_Score' in stocks_df.columns)
        
        if has_scores:
            print("\nScores already present in DataFrame, using them directly")
            # Normalize column names for the calculation function
            if 'sector_mean_score' in stocks_df.columns:
                # Convert snake_case to space-separated for compatibility
                stocks_df = stocks_df.rename(columns={
                    'sector_total_score': 'Sector Total Score',
                    'sector_mean_score': 'Sector Mean Score',
                    'security_total_score': 'Security Total Score',
                    'security_mean_score': 'Security Mean Score',
                    'sector': 'Sector',
                    'units': 'Units'
                })
            scores = calculate_portfolio_harm_scores_stocks(stocks_df)
        else:
            print("\nScores not present, calculating them first...")
            # If scores not present, calculate them first
            sector_scoring_df = fetch_sector_scoring_data()
            if not sector_scoring_df.empty:
                print(f"Sector scoring data available ({len(sector_scoring_df)} rows)")
                # Normalize column names before adding scores
                if 'sector' in stocks_df.columns:
                    stocks_df = stocks_df.rename(columns={'sector': 'Sector', 'units': 'Units'})
                stocks_df = add_scoring_columns_to_stocks(stocks_df, sector_scoring_df)
            else:
                print("WARNING: No sector scoring data available")
            scores = calculate_portfolio_harm_scores_stocks(stocks_df)
        
        print(f"\nCalculated Harm Scores:")
        print(f"  Average Score: {scores.get('average_score', 'N/A')}")
        print(f"  Total Score: {scores.get('total_score', 'N/A')}")
        print(f"  Quartile: {scores.get('quartile', 'N/A')}")
        print("=" * 50)
        
        return PortfolioHarmScores(**scores)
    except Exception as e:
        print(f"ERROR calculating stock harm scores: {type(e).__name__}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error calculating stock harm scores: {str(e)}")

@router.post("/harm-scores/bonds", response_model=PortfolioHarmScores)
async def calculate_bond_harm_scores(portfolio_request: PortfolioBondsRequest):
    """Calculate portfolio harm scores for bonds (accepts bond data from frontend)"""
    try:
        bonds = [bond.model_dump() for bond in portfolio_request.bonds]
        bonds_df = pd.DataFrame(bonds)
        
        # Convert column names if needed
        if 'Sector Mean Score' in bonds_df.columns:
            scores = calculate_portfolio_harm_scores(bonds_df)
        else:
            # If scores not present, calculate them first
            sector_scoring_df = fetch_sector_scoring_data()
            if not sector_scoring_df.empty:
                bonds_df = add_scoring_columns_to_bonds1(
                    bonds_df[['CUSIP', 'Industry Group', 'Issuer', 'Units', 'Current Price',
                             'Purchase Price', 'Coupon', 'Price Return', 'Income Return', 'Total Return']],
                    sector_scoring_df
                )
            scores = calculate_portfolio_harm_scores(bonds_df)
        
        return PortfolioHarmScores(**scores)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating bond harm scores: {str(e)}")
