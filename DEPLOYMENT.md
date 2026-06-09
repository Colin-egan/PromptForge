# PromptForge Deployment Guide

> **Complete deployment instructions for production and demo environments**

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Health Checks](#health-checks)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (tested with 3.13)
- **Node.js 18+** and npm
- **Docker** (optional, for sandbox and containerized deployment)
- **IBM watsonx.ai credentials** (API key, project ID, URL)

### 1. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd PromptForge

# Run automated setup
chmod +x setup.sh
./setup.sh
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your credentials
nano .env
```

Required environment variables:
```env
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
GRANITE_MODEL_ID=ibm/granite-3-8b-instruct
```

### 3. Start Services

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - ChromaDB (Optional):**
```bash
docker run -p 8001:8000 \
  -v $(pwd)/data/chroma:/chroma/chroma \
  -e IS_PERSISTENT=TRUE \
  chromadb/chroma:latest
```

### 4. Verify Deployment

Open browser: **http://localhost:3000**

Check health endpoint: **http://localhost:8000/api/health**

---

## 🏭 Production Deployment

### Option 1: Docker Compose (Recommended)

```bash
# Build all services
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Manual Production Setup

#### Backend Production

```bash
cd backend

# Create production virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn (production WSGI server)
pip install gunicorn
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

#### Frontend Production

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Start production server
npm start
```

---

## 🐳 Docker Deployment

### Build Images

```bash
# Build backend
cd backend
docker build -t promptforge-backend:latest .

# Build frontend
cd ../frontend
docker build -t promptforge-frontend:latest .

# Build sandbox
cd ../backend/sandbox
docker build -t promptforge-sandbox:latest .
```

### Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Individual Container Deployment

#### Backend Container

```bash
docker run -d \
  --name promptforge-backend \
  -p 8000:8000 \
  -e WATSONX_API_KEY=${WATSONX_API_KEY} \
  -e WATSONX_PROJECT_ID=${WATSONX_PROJECT_ID} \
  -e WATSONX_URL=${WATSONX_URL} \
  -v $(pwd)/data:/app/data \
  -v /var/run/docker.sock:/var/run/docker.sock \
  promptforge-backend:latest
```

#### Frontend Container

```bash
docker run -d \
  --name promptforge-frontend \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://backend:8000 \
  promptforge-frontend:latest
```

#### ChromaDB Container

```bash
docker run -d \
  --name promptforge-chroma \
  -p 8001:8000 \
  -v $(pwd)/data/chroma:/chroma/chroma \
  -e IS_PERSISTENT=TRUE \
  chromadb/chroma:latest
```

---

## ⚙️ Environment Configuration

### Backend Environment Variables

```env
# IBM watsonx.ai Configuration (Required)
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Model Configuration
GRANITE_MODEL_ID=ibm/granite-3-8b-instruct
GRANITE_EMBEDDING_MODEL=ibm/slate-125m-english-rtrvr

# ChromaDB Configuration
CHROMA_HOST=localhost
CHROMA_PORT=8001
CHROMA_COLLECTION=cadquery_examples

# Sandbox Configuration
SANDBOX_IMAGE=promptforge-sandbox:latest
SANDBOX_TIMEOUT=30
SANDBOX_MEMORY_LIMIT=2g
SANDBOX_CPU_LIMIT=2

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# CORS Configuration (for production)
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Frontend Environment Variables

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Environment
NODE_ENV=production
```

---

## 🏥 Health Checks

### Backend Health Check

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "watsonx": "connected",
  "chroma": "connected",
  "sandbox": "ready"
}
```

### Frontend Health Check

```bash
curl http://localhost:3000
```

Should return HTML page.

### ChromaDB Health Check

```bash
curl http://localhost:8001/api/v1/heartbeat
```

Expected response:
```json
{
  "nanosecond heartbeat": 1234567890
}
```

---

## 🔧 Troubleshooting

### Backend Issues

#### "Module not found" errors
```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

#### "Port 8000 already in use"
```bash
lsof -i :8000
kill -9 <PID>
```

#### "watsonx.ai connection failed"
- Verify API key in `.env`
- Check project ID is correct
- Ensure watsonx.ai URL is accessible
- Test credentials: `curl -H "Authorization: Bearer $WATSONX_API_KEY" $WATSONX_URL`

#### "ChromaDB connection failed"
```bash
# Start ChromaDB
docker run -d -p 8001:8000 chromadb/chroma:latest

# Or update CHROMA_HOST in .env if using different host
```

### Frontend Issues

#### "npm command not found"
Install Node.js from: https://nodejs.org/

#### "Port 3000 already in use"
```bash
lsof -i :3000
kill -9 <PID>
```

#### "API connection failed"
- Verify backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in frontend `.env`
- Verify CORS settings in backend

### Docker Issues

#### "Cannot connect to Docker daemon"
```bash
# Start Docker Desktop (macOS/Windows)
# Or start Docker service (Linux)
sudo systemctl start docker
```

#### "Permission denied" on docker.sock
```bash
sudo chmod 666 /var/run/docker.sock
# Or add user to docker group
sudo usermod -aG docker $USER
```

#### "Out of disk space"
```bash
# Clean up Docker
docker system prune -a
docker volume prune
```

---

## 📊 Performance Tuning

### Backend Optimization

```bash
# Increase workers for production
gunicorn app.main:app \
  --workers 8 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Frontend Optimization

```bash
# Build with optimizations
npm run build

# Analyze bundle size
npm run analyze
```

### Database Optimization

```bash
# Increase ChromaDB memory
docker run -d \
  -p 8001:8000 \
  -m 4g \
  chromadb/chroma:latest
```

---

## 🔒 Security Considerations

### Production Checklist

- [ ] Change default ports if exposed to internet
- [ ] Use HTTPS with SSL certificates
- [ ] Set up firewall rules
- [ ] Rotate API keys regularly
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerts
- [ ] Regular security updates
- [ ] Backup data directory regularly

### Recommended Security Settings

```env
# Backend .env
LOG_LEVEL=WARNING  # Reduce log verbosity
ALLOWED_ORIGINS=https://yourdomain.com  # Restrict CORS
```

---

## 📈 Monitoring

### Log Files

```bash
# Backend logs
tail -f backend/logs/app.log

# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Metrics to Monitor

- API response times
- watsonx.ai API usage
- Sandbox execution times
- Memory usage
- Disk space
- Error rates

---

## 🔄 Updates and Maintenance

### Update Dependencies

```bash
# Backend
cd backend
source .venv/bin/activate
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
```

### Database Backup

```bash
# Backup ChromaDB
tar -czf chroma-backup-$(date +%Y%m%d).tar.gz data/chroma/

# Restore
tar -xzf chroma-backup-YYYYMMDD.tar.gz
```

---

## 🌐 Cloud Deployment

### AWS Deployment

```bash
# Use AWS ECS or EC2
# Configure environment variables in AWS Systems Manager Parameter Store
# Use AWS RDS for persistent storage
```

### IBM Cloud Deployment

```bash
# Deploy to IBM Cloud Code Engine
ibmcloud ce application create \
  --name promptforge \
  --image promptforge-backend:latest \
  --env WATSONX_API_KEY=$WATSONX_API_KEY
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/
```

---

## 📞 Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Review health endpoints
3. Consult documentation in `docs/`
4. Check GitHub issues

---

**Built with IBM Bob, Granite, and watsonx.ai** 🚀