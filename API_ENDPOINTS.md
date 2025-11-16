# API Endpoints Documentation

This API is designed for frontend storage of portfolio data. The backend provides calculation and data retrieval endpoints.

## Stock & Bond Information

### Get Stock Information
**POST** `/api/portfolio/stocks/info`

Calculate stock information including prices, returns, and harm scores.

**Request Body:**
```json
{
  "ticker": "AAPL",
  "units": 100,
  "purchase_date": "2024-01-01",
  "purchase_price": 150.00  // optional, will fetch if not provided
}
```

**Response:**
```json
{
  "stock": "AAPL",
  "units": 100,
  "purchase_date": "2024-01-01",
  "purchase_price": 150.00,
  "current_price": 175.50,
  "initial_investment": 15000.00,
  "current_value": 17550.00,
  "gain_loss": 2550.00,
  "gain_loss_percentage": 17.0,
  "sector": "Technology",
  "sector_total_score": 45.2,
  "sector_mean_score": 0.45,
  "security_total_score": 45.0,
  "security_mean_score": 0.45
}
```

### Get Bond Information
**POST** `/api/portfolio/bonds/info`

Calculate bond information including prices, returns, and harm scores.

**Request Body:**
```json
{
  "cusip": "910047AG4",
  "units": 10000,
  "purchase_price": 100.0,
  "purchase_date": "2024-01-01"
}
```

**Response:**
```json
{
  "cusip": "910047AG4",
  "name": "Bond Name",
  "industry_group": "Financial Services",
  "issuer": "Issuer Name",
  "units": 10000,
  "purchase_price": 100.0,
  "purchase_date": "2024-01-01",
  "current_price": 102.5,
  "coupon": 3.5,
  "maturity_date": "2030-12-31",
  "ytm": 3.2,
  "market_value": 10250.0,
  "total_cost": 10000.0,
  "price_return": 250.0,
  "income_return": 350.0,
  "total_return": 600.0,
  "sector_total_score": 38.5,
  "sector_mean_score": 0.38,
  "security_total_score": 3800.0,
  "security_mean_score": 0.38
}
```

## Harm Score Calculation

### Calculate Stock Portfolio Harm Scores
**POST** `/api/portfolio/harm-scores/stocks`

Calculate portfolio-level harm scores from a list of stocks stored in frontend.

**Request Body:**
```json
{
  "stocks": [
    {
      "stock": "AAPL",
      "units": 100,
      "purchase_date": "2024-01-01",
      "purchase_price": 150.00,
      "current_price": 175.50,
      "initial_investment": 15000.00,
      "current_value": 17550.00,
      "gain_loss": 2550.00,
      "gain_loss_percentage": 17.0,
      "sector": "Technology",
      "sector_total_score": 45.2,
      "sector_mean_score": 0.45,
      "security_total_score": 45.0,
      "security_mean_score": 0.45
    }
  ]
}
```

**Response:**
```json
{
  "average_score": 45.2,
  "total_score": 45.0,
  "quartile": "Quartile 2"
}
```

### Calculate Bond Portfolio Harm Scores
**POST** `/api/portfolio/harm-scores/bonds`

Calculate portfolio-level harm scores from a list of bonds stored in frontend.

**Request Body:**
```json
{
  "bonds": [
    {
      "cusip": "910047AG4",
      "name": "Bond Name",
      "industry_group": "Financial Services",
      "issuer": "Issuer Name",
      "units": 10000,
      "purchase_price": 100.0,
      "purchase_date": "2024-01-01",
      "current_price": 102.5,
      "coupon": 3.5,
      "maturity_date": "2030-12-31",
      "ytm": 3.2,
      "market_value": 10250.0,
      "total_cost": 10000.0,
      "price_return": 250.0,
      "income_return": 350.0,
      "total_return": 600.0,
      "sector_total_score": 38.5,
      "sector_mean_score": 0.38,
      "security_total_score": 3800.0,
      "security_mean_score": 0.38
    }
  ]
}
```

**Response:**
```json
{
  "average_score": 38.5,
  "total_score": 3800.0,
  "quartile": "Quartile 1"
}
```

## Sectors

### Get Available Sectors
**GET** `/api/sectors/list`

Get list of all available sectors from database.

**Response:**
```json
["Technology", "Financial Services", "Healthcare", ...]
```

### Get Sector Data (Sector Equity Profile)
**GET** `/api/sectors/{sector}/data`

Get detailed sector equity data.

**Response:**
```json
[
  {
    "sector": "Technology",
    "sdh_category": "Economic Stability",
    "sdh_indicator": "Income Inequality",
    "harm_description": "Description",
    "harm_typology": "Economic Harm",
    "claim_quantification": "Quantification",
    "total_magnitude": 8.5,
    "reach": 7.2,
    "harm_direction": 6.8,
    "harm_duration": 9.1,
    "direct_indirect_1": "Direct",
    "direct_indirect": "Direct",
    "core_peripheral": "Core",
    "total_score": 12.5,
    "citation_1": "Citation 1",
    "citation_2": "Citation 2"
  }
]
```

### Get Formatted Sector Profile
**GET** `/api/sectors/{sector}/profile`

Get formatted Sector Equity Profile with display-friendly column names.

**Response:** Same as `/data` but with formatted column names (e.g., "SDH Indicator" instead of "SDH_Indicator")

### Get Sankey Diagram Data
**GET** `/api/sectors/{sector}/sankey?subtract_max=true&max_value=15`

Get data for creating Sankey diagram.

**Query Parameters:**
- `subtract_max` (bool, default: true): Whether to subtract from max value
- `max_value` (float, default: 15): Maximum value for subtraction

**Response:**
```json
{
  "node_list": ["Technology", "Economic Harm", "Income Inequality", ...],
  "source": [0, 1, 2, ...],
  "target": [1, 2, 3, ...],
  "value": [12.5, 8.3, 6.2, ...],
  "node_colors": ["#1f77b4", "#ff7f0e", "#2ca02c", ...],
  "level_colors": {
    "sector": "#1f77b4",
    "harm_typology": "#ff7f0e",
    "sdh_category": "#2ca02c",
    "sdh_indicator": "#d62728"
  }
}
```

### Get Sector Info
**GET** `/api/sectors/{sector}/info`

Get sector scoring information.

**Response:**
```json
{
  "sector": "Technology",
  "total_score": 1250.5,
  "mean_score": 0.85
}
```

## Research Alerts

### Get New Racial Justice Research Alerts
**GET** `/api/research-alerts`

Get research alerts from JSON file.

**Response:**
```json
[
  {
    "Sector": "Technology",
    "SDH_Category": "Economic Stability",
    "SDH_Indicator": "Income Inequality",
    "Harm_Description": "Description of harm",
    "Original_Claim_Quantification": "Original claim",
    "New_Evidence": "New evidence from research"
  }
]
```

## Reports

### Generate PDF Report
**POST** `/api/reports/pdf`

Generate PDF report for a sector.

**Request Body:**
```json
{
  "sector": "Technology",
  "portfolio_harm_scores": {
    "average_score": 45.2,
    "total_score": 45.0,
    "quartile": "Quartile 2"
  }
}
```

**Response:** PDF file download

## Holdings

### Get Kataly Holdings
**GET** `/api/holdings/kataly`

Get Kataly holdings from database.

**Response:**
```json
[
  {
    "Security": "Security Name",
    "Quantity": 10000,
    "Sector": "Technology",
    ...
  }
]
```

