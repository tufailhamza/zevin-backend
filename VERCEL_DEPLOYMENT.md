# Deploying to Vercel

This guide will help you deploy your FastAPI backend to Vercel.

## Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. Vercel CLI installed (optional, for CLI deployment)
3. Your project pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Step 1: Install Vercel CLI (Optional)

If you want to deploy from the command line:

```bash
npm i -g vercel
```

## Step 2: Environment Variables

Before deploying, you'll need to set up environment variables in Vercel:

1. Go to your Vercel project settings
2. Navigate to "Environment Variables"
3. Add the following variables (if you want to use them instead of hardcoded values):

```
DATABASE_USER=doadmin
DATABASE_PASSWORD=AVNS_xKVgSkiz4gkauzSux86
DATABASE_HOST=db-mysql-nyc3-25707-do-user-19616823-0.l.db.ondigitalocean.com
DATABASE_PORT=25060
DATABASE_NAME=defaultdb
```

**Note:** Currently, database credentials are hardcoded in `app/database.py`. For better security, consider moving them to environment variables.

## Step 3: Deploy via Vercel Dashboard

1. Go to https://vercel.com/new
2. Import your Git repository
3. Vercel will automatically detect the Python project
4. Configure:
   - **Framework Preset:** Other
   - **Root Directory:** ./
   - **Build Command:** (leave empty - Vercel will auto-install dependencies)
   - **Output Directory:** (leave empty)
   - **Install Command:** `pip install -r requirements.txt` (optional, Vercel does this automatically)
5. Click "Deploy"

**Important:** Make sure your repository is pushed to GitHub/GitLab/Bitbucket before importing.

## Step 4: Deploy via CLI (Alternative)

If you prefer using the CLI:

```bash
# Login to Vercel
vercel login

# Deploy (first time)
vercel

# Deploy to production
vercel --prod
```

## Step 5: Verify Deployment

After deployment, Vercel will provide you with a URL like:
- `https://your-project-name.vercel.app`

Test your endpoints:
- `https://your-project-name.vercel.app/` - Root endpoint
- `https://your-project-name.vercel.app/health` - Health check
- `https://your-project-name.vercel.app/api/portfolio/stocks/info` - Stock info endpoint

## Important Notes

1. **Serverless Functions:** Vercel runs your FastAPI app as serverless functions. Each API route becomes a separate function.

2. **Cold Starts:** The first request after inactivity may be slower due to cold starts.

3. **Function Timeout:** Vercel has execution time limits:
   - Hobby plan: 10 seconds
   - Pro plan: 60 seconds
   - Enterprise: Custom

4. **Database Connections:** Make sure your database allows connections from Vercel's IP addresses. You may need to whitelist Vercel IPs or allow all IPs in your database settings.

5. **CORS:** Update CORS settings in `app/main.py` to allow your frontend domain:
   ```python
   allow_origins=["https://your-frontend.vercel.app"]
   ```

## Troubleshooting

### Issue: Import errors
- Make sure all dependencies are in `requirements.txt`
- Check that Python version is compatible (3.11 recommended)

### Issue: Database connection errors
- Verify database credentials
- Check if database allows external connections
- Ensure firewall rules allow Vercel IPs

### Issue: Timeout errors
- Optimize slow endpoints
- Consider using background jobs for heavy operations
- Upgrade to Pro plan for longer timeouts

### Issue: Module not found
- Ensure all imports use relative paths correctly
- Check that `api/index.py` correctly imports from `app.main`

## Updating Deployment

After making changes:

1. **Via Git:** Push to your repository, Vercel will auto-deploy
2. **Via CLI:** Run `vercel --prod`

## Custom Domain

To use a custom domain:

1. Go to Project Settings > Domains
2. Add your domain
3. Follow DNS configuration instructions

