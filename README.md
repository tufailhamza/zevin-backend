# Corporate Racial Justice Intelligence API

FastAPI backend for portfolio management and racial equity analysis. This API provides endpoints for managing stock and bond portfolios, calculating harm scores, and generating reports.

## Features

- **Stock/Bond Information**: Calculate stock and bond information including prices, returns, and harm scores
- **Harm Score Calculation**: Calculate portfolio-level racial equity harm scores from frontend-stored data
- **Sector Analysis**: Get detailed sector data, Sankey diagram data, and Sector Equity Profiles
- **Report Generation**: Generate PDF reports for sectors
- **Research Alerts**: Get New Racial Justice Research Alert data
- **Kataly Holdings**: Retrieve Kataly holdings from database

**Note**: Portfolio data (stocks and bonds) is stored in the frontend. The backend provides calculation and data retrieval endpoints.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Stock & Bond Information

- `POST /api/portfolio/stocks/info` - Calculate stock information and harm scores
- `POST /api/portfolio/bonds/info` - Calculate bond information and harm scores

### Harm Score Calculation

- `POST /api/portfolio/harm-scores/stocks` - Calculate portfolio harm scores from stock list
- `POST /api/portfolio/harm-scores/bonds` - Calculate portfolio harm scores from bond list

### Sectors

- `GET /api/sectors/list` - Get list of available sectors
- `GET /api/sectors/{sector}/data` - Get detailed sector equity data
- `GET /api/sectors/{sector}/profile` - Get formatted Sector Equity Profile
- `GET /api/sectors/{sector}/sankey` - Get Sankey diagram data
- `GET /api/sectors/{sector}/info` - Get sector scoring information

### Research Alerts

- `GET /api/research-alerts` - Get New Racial Justice Research Alert data

### Reports

- `POST /api/reports/pdf` - Generate PDF report

### Holdings

- `GET /api/holdings/kataly` - Get Kataly holdings from database

See [API_ENDPOINTS.md](API_ENDPOINTS.md) for detailed endpoint documentation with request/response examples.

## React Frontend Integration

The API is configured with CORS to work with React frontends. **Portfolio data is stored in the frontend**, and the backend provides calculation endpoints.

**Example: Get Stock Information**
```javascript
// Calculate stock info (frontend stores the result)
const response = await fetch('http://localhost:8000/api/portfolio/stocks/info', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    ticker: 'AAPL',
    units: 100,
    purchase_date: '2024-01-01',
  }),
});

const stockInfo = await response.json();
// Store stockInfo in your frontend state/context
```

**Example: Calculate Harm Scores**
```javascript
// Calculate harm scores from frontend-stored portfolio
const response = await fetch('http://localhost:8000/api/portfolio/harm-scores/stocks', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    stocks: yourStocksArray, // Array of stock objects from frontend
  }),
});

const harmScores = await response.json();
```

## Development

The API uses FastAPI with automatic OpenAPI documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Notes

- Portfolio data is currently stored in-memory. For production, consider using a database.
- API keys should be stored in environment variables, not hardcoded.
- The CORS configuration allows all origins in development. Restrict this in production.

