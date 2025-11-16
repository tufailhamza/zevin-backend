from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
import uvicorn
from app.routers import portfolio, sectors, reports, holdings, research

app = FastAPI(
    title="Corporate Racial Justice Intelligence API",
    description="FastAPI backend for portfolio management and racial equity analysis",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(sectors.router, prefix="/api/sectors", tags=["sectors"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(holdings.router, prefix="/api/holdings", tags=["holdings"])
app.include_router(research.router, prefix="/api", tags=["research"])

@app.get("/")
async def root():
    return {"message": "Corporate Racial Justice Intelligence API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

