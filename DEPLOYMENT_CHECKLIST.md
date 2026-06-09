# PromptForge Deployment Checklist

Use this checklist to ensure a smooth deployment to production.

## Pre-Deployment Checklist

### 1. Code Preparation
- [ ] All code committed to Git
- [ ] No sensitive data in code (API keys, passwords)
- [ ] `.env` files in `.gitignore`
- [ ] All tests passing locally
- [ ] Documentation updated

### 2. Accounts Setup
- [ ] GitHub account created
- [ ] Vercel account created (free tier)
- [ ] Railway account created (free $5 credit)
- [ ] IBM watsonx.ai credentials obtained:
  - [ ] API Key
  - [ ] Project ID
  - [ ] URL (usually `https://us-south.ml.cloud.ibm.com`)

### 3. Repository Setup
- [ ] Code pushed to GitHub
- [ ] Repository is public or accessible to Vercel/Railway
- [ ] Main branch is `main` or `master`

---

## Railway Backend Deployment

### Step 1: Create Project
- [ ] Logged into Railway
- [ ] Created new project from GitHub repo
- [ ] Repository connected successfully

### Step 2: Configure Backend Service
- [ ] Environment variables added:
  - [ ] `WATSONX_API_KEY`
  - [ ] `WATSONX_PROJECT_ID`
  - [ ] `WATSONX_URL`
  - [ ] `GRANITE_MODEL_ID`
  - [ ] `API_HOST=0.0.0.0`
  - [ ] `API_PORT=$PORT`
  - [ ] `LOG_LEVEL=INFO`
- [ ] Custom domain generated
- [ ] Backend URL copied for Vercel

### Step 3: Add Chroma Database
- [ ] New empty service created
- [ ] Named `chroma`
- [ ] Docker image set to `chromadb/chroma:latest`
- [ ] Volume added:
  - [ ] Mount path: `/chroma/chroma`
  - [ ] Size: 1GB
- [ ] Environment variables added:
  - [ ] `IS_PERSISTENT=TRUE`
  - [ ] `ANONYMIZED_TELEMETRY=FALSE`

### Step 4: Verify Backend
- [ ] Deployment completed successfully
- [ ] No errors in logs
- [ ] Health endpoint responding: `curl https://your-backend.railway.app/api/health`
- [ ] Returns: `{"status":"healthy"}`

---

## Vercel Frontend Deployment

### Step 1: Create Project
- [ ] Logged into Vercel
- [ ] Imported GitHub repository
- [ ] Framework detected as Next.js

### Step 2: Configure Build Settings
- [ ] Root directory set to `frontend`
- [ ] Build command: `npm run build`
- [ ] Output directory: `.next`
- [ ] Install command: `npm install`

### Step 3: Add Environment Variables
- [ ] `NEXT_PUBLIC_API_URL` set to Railway backend URL
- [ ] Format: `https://your-backend.railway.app` (no trailing slash)

### Step 4: Deploy
- [ ] Deployment triggered
- [ ] Build completed successfully
- [ ] No build errors
- [ ] Vercel URL generated (e.g., `promptforge.vercel.app`)

### Step 5: Verify Frontend
- [ ] Frontend loads at Vercel URL
- [ ] No console errors in browser
- [ ] Chat interface visible
- [ ] 3D viewer canvas renders

---

## Database Initialization

### Option A: Local Ingestion
- [ ] Environment variables set locally:
  - [ ] `WATSONX_API_KEY`
  - [ ] `WATSONX_PROJECT_ID`
  - [ ] `WATSONX_URL`
  - [ ] `CHROMA_HOST` (Railway backend URL)
  - [ ] `CHROMA_PORT=443`
- [ ] Ran: `cd backend && python -m app.scripts.ingest`
- [ ] Ingestion completed without errors
- [ ] Examples loaded into Chroma

### Option B: Railway Ingestion
- [ ] One-off command added in Railway
- [ ] Command: `python -m app.scripts.ingest`
- [ ] Executed successfully
- [ ] Logs show successful ingestion

---

## Integration Testing

### Test 1: Basic Generation
- [ ] Visited Vercel URL
- [ ] Entered prompt: "Create a simple phone holder"
- [ ] Message sent successfully
- [ ] Response received from backend
- [ ] 3D model generated and displayed
- [ ] No errors in browser console

### Test 2: Parameter Sliders
- [ ] Parameter sliders appeared
- [ ] Moved a slider
- [ ] Model updated in real-time
- [ ] No errors or lag

### Test 3: Conversational Editing
- [ ] Sent follow-up: "Make it taller"
- [ ] Model updated (not regenerated from scratch)
- [ ] Changes applied correctly

### Test 4: Print Analysis
- [ ] Clicked "Analyze Printability" (if implemented)
- [ ] Analysis report generated
- [ ] Recommendations displayed

### Test 5: Export
- [ ] Clicked "Download STL"
- [ ] File downloaded successfully
- [ ] File opens in slicer software
- [ ] Model is manifold and printable

---

## Post-Deployment Configuration

### CORS Configuration
- [ ] Added Vercel domain to Railway backend CORS:
  - [ ] `CORS_ORIGINS=https://promptforge.vercel.app,https://*.vercel.app`
- [ ] Backend redeployed
- [ ] CORS errors resolved

### Custom Domain (Optional)
- [ ] Custom domain purchased
- [ ] DNS configured for Vercel
- [ ] SSL certificate provisioned
- [ ] Custom domain working
- [ ] Updated `NEXT_PUBLIC_API_URL` if needed

### Monitoring Setup
- [ ] Vercel Analytics enabled
- [ ] Railway metrics dashboard reviewed
- [ ] Error tracking configured (optional: Sentry)
- [ ] Uptime monitoring configured (optional: UptimeRobot)

---

## Security Checklist

- [ ] No API keys in code or Git history
- [ ] Environment variables properly secured
- [ ] CORS configured correctly (not `*`)
- [ ] Rate limiting enabled (if implemented)
- [ ] HTTPS enforced on both services
- [ ] Docker sandbox properly isolated
- [ ] Non-root user in Docker containers

---

## Performance Optimization

- [ ] Frontend:
  - [ ] Images optimized
  - [ ] Code splitting enabled
  - [ ] Lazy loading implemented
  - [ ] Service worker configured (optional)
- [ ] Backend:
  - [ ] Connection pooling enabled
  - [ ] RAG results cached
  - [ ] Async operations used
  - [ ] Database queries optimized

---

## Documentation Updates

- [ ] README.md updated with deployment URLs
- [ ] DEPLOYMENT_GUIDE.md reviewed
- [ ] Environment variable examples updated
- [ ] API documentation reflects production URLs
- [ ] Demo video includes production deployment

---

## Final Verification

### Functionality
- [ ] All core features working
- [ ] No critical bugs
- [ ] Performance acceptable (< 5s for generation)
- [ ] Mobile responsive (if applicable)

### Reliability
- [ ] Services stay up for 24 hours
- [ ] No memory leaks
- [ ] Error handling works correctly
- [ ] Graceful degradation on failures

### User Experience
- [ ] Loading states clear
- [ ] Error messages helpful
- [ ] UI intuitive
- [ ] 3D viewer smooth

---

## Rollback Plan

### If Deployment Fails

**Frontend (Vercel):**
1. Go to Vercel → Deployments
2. Find last working deployment
3. Click "Promote to Production"
4. Instant rollback

**Backend (Railway):**
1. Go to Railway → Deployments
2. Find last working deployment
3. Click "Redeploy"
4. Wait 2-3 minutes

### Emergency Contacts
- Railway Support: https://railway.app/help
- Vercel Support: https://vercel.com/support
- IBM watsonx Support: https://www.ibm.com/support

---

## Cost Monitoring

### First Month
- [ ] Vercel usage tracked (should be $0)
- [ ] Railway usage tracked (~$5-10)
- [ ] watsonx.ai usage tracked (varies)
- [ ] Total cost within budget

### Ongoing
- [ ] Set up billing alerts
- [ ] Review usage weekly
- [ ] Optimize if costs exceed expectations

---

## Submission Checklist (IBM AI Builders Challenge)

- [ ] Deployment URLs documented
- [ ] Demo video recorded showing live deployment
- [ ] Architecture diagram updated
- [ ] Bob usage documented
- [ ] Code repository public
- [ ] README.md complete
- [ ] All required documentation included
- [ ] Submission form completed

---

## Success Criteria

✅ **Deployment is successful when:**
- Frontend loads at Vercel URL
- Backend responds at Railway URL
- Users can generate 3D models
- Models can be downloaded as STL
- No critical errors in logs
- Performance is acceptable
- Costs are within budget

---

**Deployment Date:** _______________

**Deployed By:** _______________

**Production URLs:**
- Frontend: _______________
- Backend: _______________

**Notes:**
_______________________________________________
_______________________________________________
_______________________________________________