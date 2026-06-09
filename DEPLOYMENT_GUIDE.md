# PromptForge Deployment Guide

This guide walks you through deploying PromptForge to production using **Vercel** (frontend) and **Railway** (backend).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Vercel (Global CDN)                  │
│                  Next.js Frontend                       │
│                  promptforge.vercel.app                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ API Requests
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Railway (US Region)                    │
│         FastAPI + Docker Sandbox + Chroma               │
│         promptforge-backend.railway.app                 │
└─────────────────────────────────────────────────────────┘
                     │
                     │ AI Requests
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  IBM watsonx.ai                         │
│                  Granite 3.x Models                     │
└─────────────────────────────────────────────────────────┘
```

---

## Prerequisites

Before you begin, ensure you have:

1. **GitHub Account** - Your code must be in a GitHub repository
2. **Vercel Account** - Sign up at [vercel.com](https://vercel.com) (free)
3. **Railway Account** - Sign up at [railway.app](https://railway.app) (free $5 credit, then ~$5-10/month)
4. **IBM watsonx.ai Credentials**:
   - API Key
   - Project ID
   - URL (usually `https://us-south.ml.cloud.ibm.com`)

---

## Part 1: Deploy Backend to Railway

### Step 1: Push Code to GitHub

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Prepare for deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/promptforge.git
git branch -M main
git push -u origin main
```

### Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub account
5. Select your `promptforge` repository
6. Railway will detect the `railway.json` configuration

### Step 3: Configure Backend Service

1. In Railway dashboard, click on your project
2. Click **"Variables"** tab
3. Add the following environment variables:

```bash
# IBM watsonx.ai Credentials
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Model Configuration
GRANITE_MODEL_ID=ibm/granite-3-8b-instruct

# Chroma Configuration (Railway internal)
CHROMA_HOST=chroma
CHROMA_PORT=8000

# API Configuration
API_HOST=0.0.0.0
API_PORT=$PORT
LOG_LEVEL=INFO

# Sandbox Configuration
SANDBOX_IMAGE=promptforge-sandbox:latest
```

### Step 4: Add Chroma Database Service

1. In Railway project, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"** (we'll use volume for Chroma)
3. Actually, for Chroma, click **"+ New"** → **"Empty Service"**
4. Name it `chroma`
5. In Settings, set:
   - **Docker Image**: `chromadb/chroma:latest`
   - **Port**: `8000`
6. Add environment variables:
   ```bash
   IS_PERSISTENT=TRUE
   ANONYMIZED_TELEMETRY=FALSE
   ```
7. Add a **Volume**:
   - Mount Path: `/chroma/chroma`
   - Size: 1GB (free tier)

### Step 5: Configure Networking

1. In your backend service, go to **"Settings"**
2. Under **"Networking"**, click **"Generate Domain"**
3. Copy the generated URL (e.g., `promptforge-backend.up.railway.app`)
4. Save this URL - you'll need it for Vercel

### Step 6: Deploy Backend

Railway will automatically deploy when you push to GitHub. To manually trigger:

1. Click **"Deployments"** tab
2. Click **"Deploy"**
3. Wait for build to complete (~5-10 minutes first time)
4. Check logs for any errors

### Step 7: Test Backend

```bash
# Test health endpoint
curl https://your-backend-url.railway.app/api/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}
```

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Create Vercel Project

1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Vercel will auto-detect Next.js

### Step 2: Configure Build Settings

Vercel should auto-detect these, but verify:

- **Framework Preset**: Next.js
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `.next`
- **Install Command**: `npm install`

### Step 3: Add Environment Variables

In Vercel project settings, add:

```bash
# Backend API URL (from Railway)
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

**Important**: Replace `your-backend-url.railway.app` with your actual Railway backend URL.

### Step 4: Deploy Frontend

1. Click **"Deploy"**
2. Wait for build (~2-3 minutes)
3. Vercel will provide a URL like `promptforge.vercel.app`

### Step 5: Update Backend CORS

Go back to Railway and add to backend environment variables:

```bash
# Add your Vercel URL to allowed origins
CORS_ORIGINS=https://promptforge.vercel.app,https://*.vercel.app
```

Redeploy the backend service.

---

## Part 3: Initialize RAG Database

After both services are deployed, you need to populate the Chroma vector database with examples.

### Option A: Run Ingestion Script Locally

```bash
# Set environment variables
export WATSONX_API_KEY=your_key
export WATSONX_PROJECT_ID=your_project_id
export WATSONX_URL=https://us-south.ml.cloud.ibm.com
export CHROMA_HOST=your-backend-url.railway.app
export CHROMA_PORT=443

# Run ingestion
cd backend
python -m app.scripts.ingest
```

### Option B: Run Ingestion on Railway

1. In Railway backend service, go to **"Settings"**
2. Under **"Deploy"**, add a **"One-off Command"**:
   ```bash
   python -m app.scripts.ingest
   ```
3. This will run once and populate the database

---

## Part 4: Verify Deployment

### Test Complete Workflow

1. Visit your Vercel URL: `https://promptforge.vercel.app`
2. Try generating a model:
   ```
   "Create a simple phone holder with a 10mm base"
   ```
3. Verify:
   - ✅ Chat interface loads
   - ✅ Message is sent to backend
   - ✅ Code is generated
   - ✅ 3D model appears in viewer
   - ✅ Parameter sliders work

### Check Logs

**Railway Backend Logs:**
1. Go to Railway project
2. Click backend service
3. Click **"Deployments"** → **"View Logs"**
4. Look for errors or warnings

**Vercel Frontend Logs:**
1. Go to Vercel project
2. Click **"Deployments"**
3. Click on latest deployment
4. Click **"Functions"** to see API route logs

---

## Part 5: Custom Domain (Optional)

### Add Custom Domain to Vercel

1. In Vercel project, go to **"Settings"** → **"Domains"**
2. Add your domain (e.g., `promptforge.com`)
3. Follow DNS configuration instructions
4. Vercel will auto-provision SSL certificate

### Add Custom Domain to Railway

1. In Railway backend service, go to **"Settings"** → **"Networking"**
2. Click **"Custom Domain"**
3. Add subdomain (e.g., `api.promptforge.com`)
4. Update DNS with provided CNAME record
5. Update Vercel environment variable:
   ```bash
   NEXT_PUBLIC_API_URL=https://api.promptforge.com
   ```

---

## Cost Breakdown

### Free Tier (Good for Demo/Testing)

| Service | Free Tier | Limits |
|---------|-----------|--------|
| **Vercel** | Free forever | 100GB bandwidth/month, unlimited deployments |
| **Railway** | $5 credit | ~500 hours/month, then $5-10/month |
| **watsonx.ai** | Varies | Check IBM pricing |

**Total**: ~$5-15/month after free credits

### Production Tier (For Real Users)

| Service | Cost | Features |
|---------|------|----------|
| **Vercel Pro** | $20/month | Unlimited bandwidth, analytics, team features |
| **Railway Pro** | $10-30/month | More resources, better performance |
| **watsonx.ai** | Pay-as-you-go | Based on token usage |

**Total**: ~$30-80/month

---

## Monitoring & Maintenance

### Set Up Monitoring

1. **Vercel Analytics** (built-in):
   - Go to project → **"Analytics"**
   - Monitor page views, performance, errors

2. **Railway Metrics** (built-in):
   - Go to service → **"Metrics"**
   - Monitor CPU, memory, network usage

3. **watsonx.ai Usage**:
   - Check IBM Cloud dashboard for token usage
   - Set up billing alerts

### Regular Maintenance

- **Weekly**: Check error logs in both Vercel and Railway
- **Monthly**: Review usage and costs
- **Quarterly**: Update dependencies (`npm update`, `pip install -U`)
- **As needed**: Scale Railway resources if performance degrades

---

## Troubleshooting

### Frontend Issues

**Problem**: "Failed to fetch" errors
- **Solution**: Check `NEXT_PUBLIC_API_URL` in Vercel environment variables
- **Solution**: Verify Railway backend is running (check logs)
- **Solution**: Check CORS settings in backend

**Problem**: 3D model not loading
- **Solution**: Check browser console for errors
- **Solution**: Verify GLB file is being generated (check backend logs)

### Backend Issues

**Problem**: "watsonx.ai authentication failed"
- **Solution**: Verify `WATSONX_API_KEY` is correct in Railway
- **Solution**: Check API key hasn't expired
- **Solution**: Verify project ID is correct

**Problem**: "Chroma connection failed"
- **Solution**: Ensure Chroma service is running in Railway
- **Solution**: Check `CHROMA_HOST` and `CHROMA_PORT` variables
- **Solution**: Verify volume is mounted correctly

**Problem**: "Docker sandbox timeout"
- **Solution**: Increase Railway memory allocation (Settings → Resources)
- **Solution**: Optimize CadQuery code generation
- **Solution**: Check if Docker socket is accessible

### Performance Issues

**Problem**: Slow response times
- **Solution**: Upgrade Railway plan for more resources
- **Solution**: Enable caching for RAG results
- **Solution**: Use Vercel Edge Functions for API routes

**Problem**: High costs
- **Solution**: Implement rate limiting
- **Solution**: Cache common model generations
- **Solution**: Optimize Granite token usage (lower max_tokens)

---

## Rollback Procedure

### Rollback Frontend (Vercel)

1. Go to Vercel project → **"Deployments"**
2. Find previous working deployment
3. Click **"..."** → **"Promote to Production"**
4. Instant rollback (no downtime)

### Rollback Backend (Railway)

1. Go to Railway project → backend service
2. Click **"Deployments"**
3. Find previous working deployment
4. Click **"..."** → **"Redeploy"**
5. Wait ~2-3 minutes for redeployment

---

## Security Best Practices

1. **Never commit secrets**:
   - Use `.env.example` for templates
   - Keep `.env` in `.gitignore`
   - Use environment variables in Vercel/Railway

2. **Rotate API keys regularly**:
   - Update watsonx.ai keys every 90 days
   - Update in both Railway and local `.env`

3. **Enable rate limiting**:
   - Add rate limiting middleware in FastAPI
   - Use Vercel's built-in DDoS protection

4. **Monitor for abuse**:
   - Check Railway logs for suspicious activity
   - Set up alerts for unusual usage patterns

5. **Keep dependencies updated**:
   - Run `npm audit` and `pip-audit` regularly
   - Update to latest stable versions

---

## Next Steps

After successful deployment:

1. ✅ Test all features thoroughly
2. ✅ Set up monitoring and alerts
3. ✅ Configure custom domain (optional)
4. ✅ Share your deployment URL
5. ✅ Submit to IBM AI Builders Challenge!

---

## Support

- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **watsonx.ai Docs**: https://www.ibm.com/docs/en/watsonx-as-a-service

For PromptForge-specific issues, check the main README.md or open a GitHub issue.

---

**Made with Bob** 🤖