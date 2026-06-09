# Terminal Commands for Manual Setup

Copy and paste these commands into your Mac terminal, one section at a time.

---

## Step 1: Navigate to Project Directory

```bash
cd "/Users/colinegan/Downloads/IBM inovate ai challenge/PromptForge"
```

---

## Step 2: Set Up Backend

```bash
# Go to backend directory
cd backend

# Create Python virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install Python dependencies (this takes 2-3 minutes)
pip install -r requirements.txt

# Go back to project root
cd ..
```

---

## Step 3: Set Up Frontend

```bash
# Go to frontend directory
cd frontend

# Install Node.js dependencies (this takes 2-3 minutes)
npm install

# Go back to project root
cd ..
```

---

## Step 4: Create Environment File

```bash
# Copy the example environment file
cp .env.example .env

# Open the .env file in a text editor
nano .env
```

**In the nano editor:**
1. Find these lines:
   ```
   WATSONX_API_KEY=your_api_key_here
   WATSONX_PROJECT_ID=your_project_id_here
   ```
2. Replace `your_api_key_here` and `your_project_id_here` with your actual credentials
3. Press `Ctrl+X` to exit
4. Press `Y` to save
5. Press `Enter` to confirm

**Don't have watsonx.ai credentials?** You can skip this for now and run in demo mode.

---

## Step 5: Start the Backend (Terminal Window 1)

Open a **NEW terminal window** and run:

```bash
cd "/Users/colinegan/Downloads/IBM inovate ai challenge/PromptForge/backend"
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Keep this terminal window open!** You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

## Step 6: Start the Frontend (Terminal Window 2)

Open **ANOTHER new terminal window** and run:

```bash
cd "/Users/colinegan/Downloads/IBM inovate ai challenge/PromptForge/frontend"
npm run dev
```

**Keep this terminal window open too!** You should see:
```
- Local:        http://localhost:3000
- Ready in 2.5s
```

---

## Step 7: Open in Browser

Open your web browser and go to:

```
http://localhost:3000
```

You should see the PromptForge interface!

---

## 🎯 Quick Test

Once the page loads, try typing in the chat:

```
A simple box 50mm on each side
```

Press Enter and wait 8-15 seconds for the 3D model to appear.

---

## 🛑 To Stop the Servers

When you're done:

1. Go to **Terminal Window 1** (backend) and press `Ctrl+C`
2. Go to **Terminal Window 2** (frontend) and press `Ctrl+C`

---

## 🐛 Troubleshooting

### "Command not found: python3"
Install Python from: https://www.python.org/downloads/

### "Command not found: npm"
Install Node.js from: https://nodejs.org/

### "Port 8000 already in use"
```bash
lsof -i :8000
kill -9 <PID>
```

### "Port 3000 already in use"
```bash
lsof -i :3000
kill -9 <PID>
```

### Backend shows errors about watsonx.ai
This is normal if you haven't configured credentials yet. The system will still start but AI features won't work until you add credentials to `.env`.

### Frontend won't load
Make sure both backend AND frontend are running in separate terminal windows.

---

## 📋 Summary of What You Need Open

1. **Terminal Window 1**: Backend server (port 8000)
2. **Terminal Window 2**: Frontend server (port 3000)
3. **Browser**: http://localhost:3000

---

## 🚀 Alternative: One-Command Setup

Instead of manual setup, you can run:

```bash
cd "/Users/colinegan/Downloads/IBM inovate ai challenge/PromptForge"
./setup.sh
```

This automates steps 1-4 for you!

---

**Need help?** Check QUICK_START.md or docs/SETUP.md for more details.