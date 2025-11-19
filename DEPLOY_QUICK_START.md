# Quick Start: Deploy to Vercel

## Files Created for Vercel Deployment

✅ `vercel.json` - Vercel configuration
✅ `api/index.py` - Serverless function entry point
✅ `.vercelignore` - Files to exclude from deployment

## Quick Deployment Steps

### Option 1: Via Vercel Dashboard (Recommended)

1. **Push your code to GitHub/GitLab/Bitbucket**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push
   ```

2. **Go to Vercel Dashboard**
   - Visit https://vercel.com/new
   - Click "Import Git Repository"
   - Select your repository

3. **Configure Project**
   - Framework: **Other**
   - Root Directory: **./** (default)
   - Build Command: (leave empty)
   - Output Directory: (leave empty)

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete

5. **Get Your URL**
   - Vercel will provide: `https://your-project.vercel.app`

### Option 2: Via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod
```

## Test Your Deployment

After deployment, test these endpoints:

- `https://your-project.vercel.app/` - Should return API info
- `https://your-project.vercel.app/health` - Health check
- `https://your-project.vercel.app/api/portfolio/stocks/info` - Stock endpoint

## Important Notes

⚠️ **Database Connection**: Make sure your database allows connections from Vercel's IP addresses.

⚠️ **CORS**: Update `app/main.py` to allow your frontend domain:
```python
allow_origins=["https://your-frontend.vercel.app"]
```

⚠️ **Environment Variables**: If you want to use env vars instead of hardcoded credentials, add them in Vercel Dashboard > Settings > Environment Variables.

## Troubleshooting

**Import errors?** Check that all dependencies are in `requirements.txt`

**Database connection fails?** Verify database firewall allows Vercel IPs

**Timeout errors?** Consider upgrading to Pro plan (60s timeout vs 10s on Hobby)

## Next Steps

- Set up custom domain (optional)
- Configure environment variables (recommended)
- Set up monitoring and alerts

For detailed information, see `VERCEL_DEPLOYMENT.md`

