# Vercel Size Optimization Guide

## Issue
Vercel has a 250 MB unzipped limit for serverless functions. Large dependencies like pandas, numpy, and their dependencies can exceed this limit.

## Optimizations Applied

### 1. Removed Unused Dependencies
- ✅ `plotly` - Not used in API (only in RFL.py Streamlit app)
- ✅ `mammoth` - Not used in API
- ✅ `PyMuPDF` - Not used in API  
- ✅ `Pillow` - Not used in API
- ✅ `requests-cache` - Not used in API

### 2. Kept Essential Dependencies
- ✅ `pandas` - Required for data processing
- ✅ `numpy` - Required by pandas
- ✅ `reportlab` - Required for PDF generation
- ✅ `yfinance` - Required for stock data

## If Still Too Large

### Option 1: Use Lighter Alternatives

Consider replacing heavy dependencies:

1. **Pandas alternatives:**
   - Use `polars` (faster, smaller) instead of pandas where possible
   - Or use built-in Python data structures for simple operations

2. **Numpy alternatives:**
   - Only import what you need: `from numpy import array, mean` instead of `import numpy`

### Option 2: Split into Multiple Functions

If the API is still too large, consider:
- Creating separate Vercel functions for different endpoints
- Using Vercel's monorepo support to split the project

### Option 3: Use External Services

- Move heavy processing to external services (AWS Lambda, Google Cloud Functions)
- Use database views for complex queries instead of pandas processing

### Option 4: Upgrade Vercel Plan

- Pro plan: 300 MB limit
- Enterprise: Custom limits

## Current Size Estimate

After optimizations:
- FastAPI + dependencies: ~50-80 MB
- Pandas + NumPy: ~150-200 MB
- Other dependencies: ~20-30 MB
- **Total: ~220-310 MB** (may still exceed limit)

## Recommendations

1. **Test deployment** - The optimizations should help significantly
2. **Monitor size** - Check Vercel build logs for actual size
3. **Consider alternatives** - If still too large, consider:
   - Using a different hosting platform (Railway, Render, Fly.io)
   - Splitting the application
   - Using lighter data processing libraries

