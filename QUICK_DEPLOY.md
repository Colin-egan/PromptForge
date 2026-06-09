# Quick Deploy Guide - PromptForge

Get PromptForge deployed in **15 minutes** with this streamlined guide.

## Prerequisites Checklist

- [ ] GitHub account
- [ ] Vercel account (free) - [Sign up](https://vercel.com)
- [ ] Railway account (free $5 credit) - [Sign up](https://railway.app)
- [ ] IBM watsonx.ai credentials (API key + Project ID)

---

## 🚀 5-Step Deployment

### Step 1: Push to GitHub (2 min)

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/promptforge.git
git push -u origin main
```

### Step 2: Deploy Backend to Railway (5 min)

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**
2. Select your `promptforge` repo
3. Click **Variables** and add:
   ```
   WATSONX_API_KEY=your_key
   WATSONX_PROJECT_ID=your_project_id
   WATSONX_URL=https://us-south.ml.cloud.ibm.com
   GRANITE_MODEL_ID=ibm/granite-3-8b-instruct
   ```
4. Click **Settings** → **Networking** → **Generate Domain**
5. **Copy the URL** (e.g., `promptforge-backend.up.railway.app`)

### Step 3: Add Chroma Database (2 min)

1. In Railway project, click **+ New** → **Empty Service**
2. Name it `chroma`
3. Settings → **Docker Image**: `chromadb/chroma:latest`
4. Add **Volume**: Mount path `/chroma/chroma`, Size 1GB
5. Add variables:
   ```
   IS_PERSISTENT=TRUE
   ANONYMIZED_TELEMETRY=FALSE
   ```

### Step 4: Deploy Frontend to Vercel (3 min)

1. Go to [vercel.com](https://vercel.com) → **Add New** → **Project**
2. Import your GitHub repo
3. Set **Root Directory**: `frontend`
4. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-backend-url.railway.app
   ```
   (Use the URL from Step 2)
5. Click **Deploy**

### Step 5: Initialize Database (3 min)

```bash
# Set environment variables
export WATSONX_API_KEY=your_key
export WATSONX_PROJECT_ID=your_project_id
export WATSONX_URL=https://us-south.ml.cloud.ibm.com
export CHROMA_HOST=your-railway-backend-url.railway.app
export CHROMA_PORT=443

# Run ingestion
cd backend
python -m app.scripts.ingest
```

---

## ✅ Test Your Deployment

Visit your Vercel URL (e.g., `promptforge.vercel.app`) and try:

```
"Create a simple phone holder"
```

You should see:
- ✅ Chat interface loads
- ✅ 3D model generates
- ✅ Parameter sliders appear

---

## 🐛 Quick Troubleshooting

**Frontend shows "Failed to fetch"**
→ Check `NEXT_PUBLIC_API_URL` in Vercel matches your Railway URL

**Backend shows "watsonx authentication failed"**
→ Verify `WATSONX_API_KEY` in Railway is correct

**"Chroma connection failed"**
→ Ensure Chroma service is running in Railway

---

## 📊 Cost Estimate

- **Vercel**: Free (100GB bandwidth/month)
- **Railway**: $5-10/month after free credit
- **watsonx.ai**: Pay-as-you-go (varies by usage)

**Total**: ~$5-15/month

---

## 🔗 Useful Links

- **Full Deployment Guide**: See `DEPLOYMENT_GUIDE.md`
- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **Troubleshooting**: See `DEPLOYMENT_GUIDE.md` → Troubleshooting section

---

**Need help?** Check the full `DEPLOYMENT_GUIDE.md` for detailed instructions.