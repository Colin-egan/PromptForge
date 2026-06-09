# PromptForge Setup Guide

This guide will walk you through setting up PromptForge for local development.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** 20+ ([Download](https://nodejs.org/))
- **Python** 3.11+ ([Download](https://www.python.org/downloads/))
- **Docker** and Docker Compose ([Download](https://www.docker.com/products/docker-desktop))
- **Git** ([Download](https://git-scm.com/downloads))

## IBM watsonx.ai Setup

### 1. Create an IBM Cloud Account

1. Go to [IBM Cloud](https://cloud.ibm.com/registration)
2. Sign up for a free account or log in

### 2. Set Up watsonx.ai

1. Navigate to the [watsonx.ai service](https://cloud.ibm.com/catalog/services/watsonx-ai)
2. Click "Create" to provision the service
3. Once created, go to the service dashboard

### 3. Get Your API Credentials

1. In the watsonx.ai dashboard, go to **Manage** → **Access (IAM)**
2. Click **API keys** → **Create an IBM Cloud API key**
3. Name it (e.g., "PromptForge Dev") and click **Create**
4. **Copy and save the API key** (you won't be able to see it again)

### 4. Get Your Project ID

1. In watsonx.ai, create a new project or select an existing one
2. Go to **Manage** → **General**
3. Copy the **Project ID**

### 5. Note Your Region URL

Your watsonx.ai URL depends on your region:
- **US South:** `https://us-south.ml.cloud.ibm.com`
- **EU Germany:** `https://eu-de.ml.cloud.ibm.com`
- **Japan Tokyo:** `https://jp-tok.ml.cloud.ibm.com`

## Project Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/promptforge.git
cd promptforge
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Update the following values in `.env`:

```bash
WATSONX_API_KEY=your_actual_api_key_here
WATSONX_PROJECT_ID=your_actual_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com  # or your region
```

### 3. Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Build the CadQuery sandbox Docker image
cd sandbox
docker build -t promptforge-sandbox:latest .
cd ..
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# or with yarn
yarn install
```

### 5. Initialize Vector Database

```bash
# From the project root
cd backend

# Run the RAG ingestion script to populate Chroma
python -m app.rag.ingest
```

## Running the Application

### Option 1: Docker Compose (Recommended)

From the project root:

```bash
# Start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

Access the application:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Chroma DB:** http://localhost:8001

### Option 2: Manual Development Mode

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

**Terminal 3 - Chroma DB:**
```bash
docker run -p 8001:8000 \
  -v ./data/chroma:/chroma/chroma \
  -e IS_PERSISTENT=TRUE \
  chromadb/chroma:latest
```

## Verification

### 1. Check Backend Health

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "services": {
    "watsonx": "connected",
    "chroma": "connected",
    "sandbox": "ready"
  }
}
```

### 2. Test the Frontend

1. Open http://localhost:3000
2. You should see the PromptForge chat interface
3. Try a test prompt: "Create a simple box 50mm on each side"

### 3. Check Logs

```bash
# Docker Compose logs
docker-compose logs backend
docker-compose logs frontend

# Or follow logs in real-time
docker-compose logs -f
```

## Troubleshooting

### Issue: "watsonx.ai authentication failed"

**Solution:**
- Verify your `WATSONX_API_KEY` is correct
- Check that your API key hasn't expired
- Ensure you're using the correct `WATSONX_URL` for your region

### Issue: "Chroma connection refused"

**Solution:**
```bash
# Check if Chroma is running
docker ps | grep chroma

# Restart Chroma
docker-compose restart chroma

# Check Chroma logs
docker-compose logs chroma
```

### Issue: "Sandbox execution timeout"

**Solution:**
- Increase `SANDBOX_TIMEOUT` in `.env` (default: 30 seconds)
- Check Docker resource limits (CPU/memory)
- Verify the sandbox image is built: `docker images | grep promptforge-sandbox`

### Issue: "Module not found" errors in backend

**Solution:**
```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Issue: Frontend build errors

**Solution:**
```bash
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

### Issue: Port already in use

**Solution:**
```bash
# Find process using port 3000 (frontend)
lsof -i :3000
kill -9 <PID>

# Find process using port 8000 (backend)
lsof -i :8000
kill -9 <PID>
```

## Development Workflow

### Making Code Changes

1. **Backend changes:** The FastAPI server auto-reloads with `--reload` flag
2. **Frontend changes:** Next.js hot-reloads automatically
3. **Sandbox changes:** Rebuild the Docker image:
   ```bash
   cd backend/sandbox
   docker build -t promptforge-sandbox:latest .
   ```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Integration tests
cd backend
pytest tests/integration/
```

### Adding New Dependencies

**Backend:**
```bash
cd backend
source .venv/bin/activate
pip install <package-name>
pip freeze > requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install <package-name>
# or
yarn add <package-name>
```

## Data Management

### Resetting the Vector Database

```bash
# Stop services
docker-compose down

# Remove Chroma data
rm -rf data/chroma/*

# Restart and re-ingest
docker-compose up -d
cd backend
python -m app.rag.ingest
```

### Backing Up Generated Models

Generated models are stored in `data/output/`. To back up:

```bash
tar -czf models-backup-$(date +%Y%m%d).tar.gz data/output/
```

## Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment instructions.

## Getting Help

- **Documentation:** Check the [docs/](../docs/) directory
- **Issues:** Open an issue on GitHub
- **Architecture:** See [ARCHITECTURE.md](../ARCHITECTURE.md)
- **API Reference:** http://localhost:8000/docs (when running)

## Next Steps

Once setup is complete:

1. Read the [Architecture Overview](../ARCHITECTURE.md)
2. Try the [Example Prompts](./EXAMPLES.md)
3. Review the [API Documentation](./API.md)
4. Check out the [Development Guide](./DEVELOPMENT.md)

---

**Happy building! 🚀**