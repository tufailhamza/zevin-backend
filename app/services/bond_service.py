import requests
import datetime
from typing import Dict, Optional

EODHD_API_TOKEN = "681bef9cbfd8f3.10724014"  # In production, use environment variables

def get_bond_info(cusip: str) -> Optional[Dict]:
    """Fetch bond information from EODHD API"""
    url = f'https://eodhd.com/api/bond-fundamentals/{cusip}?api_token={EODHD_API_TOKEN}&fmt=json'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Handle None values - ensure strings are never None
        name = data.get('Name')
        industry_group = data.get('ClassificationData', {}).get('IndustryGroup')
        issuer = data.get('IssueData', {}).get('Issuer')
        maturity_date = data.get('Maturity_Date')
        
        bond_info = {
            'Name': name if name is not None and name != '' else 'Unknown',
            'Industry Group': industry_group if industry_group is not None and industry_group != '' else 'Unknown',
            'Issuer': issuer if issuer is not None and issuer != '' else 'Unknown',
            'Current Price': float(data.get('Price') or '0'),
            'Coupon': float(data.get('Coupon') or '0'),
            'Maturity Date': maturity_date if maturity_date is not None and maturity_date != '' else 'Unknown',
            'YTM': float(data.get('YieldToMaturity') or '0'),
        }
        
        return bond_info
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching bond data: {str(e)}")
        return None
    except (ValueError, KeyError) as e:
        print(f"Error processing bond data: {str(e)}")
        return None

def calculate_returns(bond_data: Dict) -> Dict:
    """Calculate various return metrics for a bond"""
    units = bond_data.get('Units', 0)
    current_price = bond_data.get('Current Price', 0)
    purchase_price = bond_data.get('Purchase Price', 0)
    coupon = bond_data.get('Coupon', 0)
    purchase_date = bond_data.get('Purchase Date')
    
    # Market value calculation
    market_value = units * float(current_price if current_price not in [None, 'None', ''] else 0) / 100
    total_cost = units * float(purchase_price if purchase_price not in [None, 'None', ''] else 0) / 100
    
    # Price return
    price_return = market_value - total_cost
    
    # Calculate days held
    if isinstance(purchase_date, str):
        purchase_date = datetime.datetime.strptime(purchase_date, '%Y-%m-%d').date()
    elif hasattr(purchase_date, 'date'):
        purchase_date = purchase_date.date()
    
    today = datetime.datetime.now().date()
    days_held = (today - purchase_date).days if purchase_date else 0
    
    # Calculate accrued interest (income return)
    annual_interest = units * (float(coupon) / 100)
    income_return = annual_interest * (days_held / 365) if days_held > 0 else 0
    
    # Total return
    total_return = price_return + income_return
    
    return {
        'Market Value': market_value,
        'Total Cost': total_cost,
        'Price Return': price_return,
        'Income Return': income_return,
        'Total Return': total_return,
    }

