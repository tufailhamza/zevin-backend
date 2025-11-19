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
    """Calculate stock information and scores from ticker and weight"""
    try:
        print(f"\n=== Stock Info Request ===")
        print(f"Ticker: {stock_request.ticker}")
        print(f"Weight: {stock_request.weight}%")
        
        # Get sector for the ticker
        from app.services.stock_service import get_gics_sector
        sector = get_gics_sector(stock_request.ticker)
        
        if sector == 'N/A':
            raise ValueError(f"Unable to fetch sector information for {stock_request.ticker}. Please verify the ticker symbol.")
        
        # Create stock data structure
        stock_data = {
            'Stock': stock_request.ticker,
            'Weight': stock_request.weight,
            'Sector': sector,
            'Units': stock_request.weight  # Use weight as Units for scoring calculation
        }
        
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
        
        # Security scores are the same as Sector scores
        # The weighting happens in the portfolio harm score calculation
        sector_total_score = stock_data.get('Sector Total Score', 0.0)
        sector_mean_score = stock_data.get('Sector Mean Score', 0.0)
        weight = stock_data.get('Weight', 0.0)
        
        # Security scores equal sector scores (weighting applied in portfolio calculation)
        security_total_score = sector_total_score
        security_mean_score = sector_mean_score
        
        # Debug: Print scoring values
        print(f"Scoring values for {stock_data.get('Stock')}:")
        print(f"  Sector: {stock_data.get('Sector')}")
        print(f"  Weight: {weight}%")
        print(f"  Sector Total Score: {sector_total_score}")
        print(f"  Sector Mean Score: {sector_mean_score}")
        print(f"  Security Total Score: {security_total_score}")
        print(f"  Security Mean Score: {security_mean_score}")
        
        return StockInfoResponse(
            stock=stock_data['Stock'],
            weight=weight,
            sector=stock_data['Sector'],
            sector_total_score=sector_total_score,
            sector_mean_score=sector_mean_score,
            security_total_score=security_total_score,
            security_mean_score=security_mean_score
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating stock info: {str(e)}")

@router.post("/bonds/info", response_model=BondInfoResponse)
async def get_bond_info(bond_request: BondInfoRequest):
    """Calculate bond information and scores from CUSIP and weight"""
    try:
        print(f"\n=== Bond Info Request ===")
        print(f"CUSIP: {bond_request.cusip}")
        print(f"Weight: {bond_request.weight}%")
        
        # Fetch bond info from API to get Industry Group
        from app.services.bond_service import get_bond_info as fetch_bond_info
        bond_info = fetch_bond_info(bond_request.cusip)
        
        if not bond_info:
            raise ValueError(f"Could not fetch bond information for CUSIP {bond_request.cusip}")
        
        industry_group = bond_info.get('Industry Group', 'Unknown')
        if industry_group is None or industry_group == '':
            industry_group = 'Unknown'
        
        print(f"Industry Group: {industry_group}")
        
        # Create bond data structure for scoring
        bond_data = {
            'CUSIP': bond_request.cusip,
            'Industry Group': industry_group,
            'Issuer': bond_info.get('Issuer', 'Unknown'),
            'Units': bond_request.weight,  # Use weight as Units for scoring calculation
            'Current Price': bond_info.get('Current Price', 0),
            'Purchase Price': 100.0,  # Default for scoring
            'Coupon': bond_info.get('Coupon', 0),
            'Price Return': 0.0,  # Not needed for scoring
            'Income Return': 0.0,  # Not needed for scoring
            'Total Return': 0.0  # Not needed for scoring
        }
        
        # Get sector scoring data and add scores
        sector_scoring_df = fetch_sector_scoring_data()
        print(f"Sector scoring data empty: {sector_scoring_df.empty}")
        
        if not sector_scoring_df.empty:
            bonds_df = pd.DataFrame([bond_data])
            print(f"Bonds DataFrame columns: {bonds_df.columns.tolist()}")
            
            # Select only columns that exist in the dataframe for scoring
            available_columns = ['CUSIP', 'Industry Group', 'Issuer', 'Units', 'Current Price',
                               'Purchase Price', 'Coupon', 'Price Return', 'Income Return', 'Total Return']
            columns_to_select = [col for col in available_columns if col in bonds_df.columns]
            print(f"Columns to select for scoring: {columns_to_select}")
            
            # Create a copy with only the columns needed for scoring
            scoring_df = bonds_df[columns_to_select].copy()
            
            # Add scoring columns
            scoring_df = add_scoring_columns_to_bonds1(
                scoring_df,
                sector_scoring_df
            )
            
            # Merge scoring columns back into the full DataFrame
            for col in ['Sector Total Score', 'Sector Mean Score', 'Security Total Score', 'Security Mean Score']:
                if col in scoring_df.columns:
                    bonds_df[col] = scoring_df[col].values
            
            bond_data = bonds_df.iloc[0].to_dict()
            print(f"After scoring, bond data keys: {list(bond_data.keys())}")
        else:
            # If no sector scoring data, set defaults
            bond_data['Sector Total Score'] = 0.0
            bond_data['Sector Mean Score'] = 0.0
            bond_data['Security Total Score'] = 0.0
            bond_data['Security Mean Score'] = 0.0
            print("Set default scoring values")
        
        # Security scores are the same as Sector scores
        # The weighting happens in the portfolio harm score calculation
        sector_total_score = bond_data.get('Sector Total Score', 0.0)
        sector_mean_score = bond_data.get('Sector Mean Score', 0.0)
        weight = bond_request.weight
        
        # Security scores equal sector scores (weighting applied in portfolio calculation)
        security_total_score = sector_total_score
        security_mean_score = sector_mean_score
        
        print(f"Creating BondInfoResponse:")
        print(f"  CUSIP: {bond_request.cusip}")
        print(f"  Weight: {weight}%")
        print(f"  Industry Group: {industry_group}")
        print(f"  Sector Total Score: {sector_total_score}")
        print(f"  Sector Mean Score: {sector_mean_score}")
        print(f"  Security Total Score: {security_total_score}")
        print(f"  Security Mean Score: {security_mean_score}")
        
        response = BondInfoResponse(
            cusip=bond_request.cusip,
            weight=weight,
            industry_group=industry_group,
            sector_total_score=sector_total_score,
            sector_mean_score=sector_mean_score,
            security_total_score=security_total_score,
            security_mean_score=security_mean_score
        )
        
        print("BondInfoResponse created successfully")
        return response
        
    except ValueError as e:
        print(f"ValueError in bond endpoint: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Exception in bond endpoint: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
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
            print(f"  Weight: {row.get('weight', 'N/A')}%")
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
                    'weight': 'Weight'
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
                    stocks_df = stocks_df.rename(columns={'sector': 'Sector', 'weight': 'Weight'})
                # Add a temporary Units column for scoring (use weight as units)
                if 'Weight' in stocks_df.columns and 'Units' not in stocks_df.columns:
                    stocks_df['Units'] = stocks_df['Weight']
                stocks_df = add_scoring_columns_to_stocks(stocks_df, sector_scoring_df)
                # Set Security scores equal to Sector scores
                stocks_df['Security Total Score'] = stocks_df['Sector Total Score']
                stocks_df['Security Mean Score'] = stocks_df['Sector Mean Score']
            else:
                print("WARNING: No sector scoring data available")
                # Set defaults
                stocks_df['Sector Total Score'] = 0.0
                stocks_df['Sector Mean Score'] = 0.0
                stocks_df['Security Total Score'] = 0.0
                stocks_df['Security Mean Score'] = 0.0
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
        print(f"\n=== Calculating Bond Portfolio Harm Scores ===")
        print(f"Received {len(portfolio_request.bonds)} bonds")
        
        bonds = [bond.model_dump() for bond in portfolio_request.bonds]
        bonds_df = pd.DataFrame(bonds)
        
        print(f"DataFrame shape: {bonds_df.shape}")
        print(f"DataFrame columns: {bonds_df.columns.tolist()}")
        
        # Check if scores are present (handle both snake_case and space-separated column names)
        has_scores = ('Sector Mean Score' in bonds_df.columns or 
                     'sector_mean_score' in bonds_df.columns or
                     'Sector_Mean_Score' in bonds_df.columns)
        
        if has_scores:
            print("\nScores already present in DataFrame, using them directly")
            # Normalize column names for the calculation function
            if 'sector_mean_score' in bonds_df.columns:
                # Convert snake_case to space-separated for compatibility
                bonds_df = bonds_df.rename(columns={
                    'sector_total_score': 'Sector Total Score',
                    'sector_mean_score': 'Sector Mean Score',
                    'security_total_score': 'Security Total Score',
                    'security_mean_score': 'Security Mean Score',
                    'industry_group': 'Industry Group',
                    'weight': 'Weight'
                })
            scores = calculate_portfolio_harm_scores(bonds_df)
        else:
            print("\nScores not present, calculating them first...")
            # If scores not present, calculate them first
            sector_scoring_df = fetch_sector_scoring_data()
            if not sector_scoring_df.empty:
                print(f"Sector scoring data available ({len(sector_scoring_df)} rows)")
                
                # Normalize column names before adding scores
                if 'industry_group' in bonds_df.columns:
                    bonds_df = bonds_df.rename(columns={
                        'industry_group': 'Industry Group',
                        'weight': 'Weight'
                    })
                
                # Add a temporary Units column for scoring (use weight as units)
                if 'Weight' in bonds_df.columns and 'Units' not in bonds_df.columns:
                    bonds_df['Units'] = bonds_df['Weight']
                
                # Select only columns that exist in the dataframe for scoring
                available_columns = ['CUSIP', 'Industry Group', 'Issuer', 'Units', 'Current Price',
                                   'Purchase Price', 'Coupon', 'Price Return', 'Income Return', 'Total Return']
                columns_to_select = [col for col in available_columns if col in bonds_df.columns]
                print(f"Columns to select for scoring: {columns_to_select}")
                
                if columns_to_select:
                    # Create a copy with only the columns needed for scoring
                    scoring_df = bonds_df[columns_to_select].copy()
                    
                    # Add scoring columns
                    scoring_df = add_scoring_columns_to_bonds1(
                        scoring_df,
                        sector_scoring_df
                    )
                    
                    # Merge scoring columns back into the full DataFrame
                    for col in ['Sector Total Score', 'Sector Mean Score', 'Security Total Score', 'Security Mean Score']:
                        if col in scoring_df.columns:
                            bonds_df[col] = scoring_df[col].values
                    
                    # Set Security scores equal to Sector scores
                    bonds_df['Security Total Score'] = bonds_df['Sector Total Score']
                    bonds_df['Security Mean Score'] = bonds_df['Sector Mean Score']
                else:
                    print("WARNING: No matching columns found for scoring")
                    # Set defaults
                    bonds_df['Sector Total Score'] = 0.0
                    bonds_df['Sector Mean Score'] = 0.0
                    bonds_df['Security Total Score'] = 0.0
                    bonds_df['Security Mean Score'] = 0.0
            else:
                print("WARNING: No sector scoring data available")
                # Set defaults
                bonds_df['Sector Total Score'] = 0.0
                bonds_df['Sector Mean Score'] = 0.0
                bonds_df['Security Total Score'] = 0.0
                bonds_df['Security Mean Score'] = 0.0
            
            scores = calculate_portfolio_harm_scores(bonds_df)
        
        print(f"\nCalculated Harm Scores:")
        print(f"  Average Score: {scores.get('average_score', 'N/A')}")
        print(f"  Total Score: {scores.get('total_score', 'N/A')}")
        print(f"  Quartile: {scores.get('quartile', 'N/A')}")
        print("=" * 50)
        
        return PortfolioHarmScores(**scores)
    except Exception as e:
        print(f"ERROR calculating bond harm scores: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error calculating bond harm scores: {str(e)}")
