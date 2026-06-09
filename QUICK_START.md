# PromptForge Quick Start Guide

Since the system isn't fully set up yet, here's what you need to do to run the demo:

## 🚀 Quick Setup (5 minutes)

### Step 1: Set Up Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Go back to project root
cd ..

# Copy environment template
cp .env.example .env

# Edit .env file and add your watsonx.ai credentials
# You need:
# - WATSONX_API_KEY
# - WATSONX_PROJECT_ID
# - WATSONX_URL
```

**Don't have watsonx.ai credentials?** You can still run a demo mode - see below.

### Step 3: Build Sandbox (Optional for full demo)

```bash
cd backend/sandbox
docker build -t promptforge-sandbox:latest .
cd ../..
```

### Step 4: Set Up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Go back to root
cd ..
```

### Step 5: Start Services

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
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

### Step 6: Open Browser

Go to: **http://localhost:3000**

---

## 🎯 Alternative: Demo Mode (No Setup Required)

If you don't want to set up the full system, I can show you:

### Option A: Code Examples Demo
View the generated CadQuery code examples that show what PromptForge produces:
- See `examples/few_shot/` directory
- Each JSON file contains a description + generated code
- Shows the quality of AI-generated parametric designs

### Option B: Documentation Demo
Review the comprehensive demo materials:
- **DEMO.md** - Complete demo guide with scenarios
- **DEMO_PRESENTATION.md** - 5-minute presentation script
- **README.md** - Full project overview

### Option C: Architecture Walkthrough
Understand how the system works:
- **ARCHITECTURE.md** - Technical architecture
- **IMPLEMENTATION_PLAN.md** - Development roadmap
- **BOB_LOG.md** - How IBM Bob built this

---

## 🐛 Troubleshooting

### "Port 3000 already in use"
```bash
# Find and kill the process
lsof -i :3000
kill -9 <PID>
```

### "Port 8000 already in use"
```bash
# Find and kill the process
lsof -i :8000
kill -9 <PID>
```

### "Module not found" errors
```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

### "npm command not found"
Install Node.js from: https://nodejs.org/

### "python3 not found"
Install Python from: https://www.python.org/downloads/

---

## 📊 What You'll See

Once running, you can:

1. **Type natural language descriptions:**
   - "A toothbrush holder with drainage holes"
   - "A desk organizer with three compartments"
   - "A phone stand with cable management"

2. **See 3D models generate in real-time** (8-15 seconds)

3. **Edit conversationally:**
   - "Make it wider"
   - "Add mounting holes"
   - "Round the corners"

4. **Adjust parameters with sliders**

5. **Export STL files for 3D printing**

---

## 🎬 Pre-Built Demo Materials

Even without running the system, you can present using:

### 1. Example Code Outputs
```bash
# View generated CadQuery code
cat examples/few_shot/holders/toothbrush_holder.json
cat examples/few_shot/organizers/desk_organizer.json
cat examples/few_shot/brackets/shelf_bracket.json
```

### 2. Architecture Diagrams
See README.md and ARCHITECTURE.md for visual system diagrams

### 3. Demo Scripts
Use DEMO_PRESENTATION.md for a complete 5-minute presentation

---

## 💡 Quick Demo Without Full Setup

Want to see what PromptForge generates? Here's a sample:

### Input:
```
"A wall-mounted toothbrush holder with drainage holes"
```

### Generated Code:
```python
import cadquery as cq

# Parameters
height = 100
diameter = 30
wall_thickness = 3
num_slots = 4
slot_diameter = 12

# Create main cylinder
holder = cq.Workplane("XY").cylinder(height, diameter / 2)

# Hollow out the interior
holder = holder.faces(">Z").workplane()
    .circle(diameter / 2 - wall_thickness)
    .cutThruAll()

# Create toothbrush slots
for i in range(num_slots):
    angle = i * (360 / num_slots)
    holder = (
        holder.faces(">Z")
        .workplane()
        .transformed(rotate=(0, 0, angle))
        .center(diameter / 4, 0)
        .circle(slot_diameter / 2)
        .cutBlind(-height + 10)
    )

# Add drainage holes
for i in range(num_slots):
    angle = i * (360 / num_slots)
    holder = (
        holder.faces("<Z")
        .workplane()
        .transformed(rotate=(0, 0, angle))
        .center(diameter / 4, 0)
        .circle(2)
        .cutThruAll()
    )

result = holder
```

### Output:
- ✅ Manifold, watertight geometry
- ✅ Parametric (all dimensions are variables)
- ✅ Print-ready STL
- ✅ Editable through conversation

---

## 🎯 Next Steps

Choose your path:

### Path 1: Full Setup (Recommended)
Follow Steps 1-6 above to run the complete system

### Path 2: Quick Demo
Use the pre-built demo materials in DEMO.md and DEMO_PRESENTATION.md

### Path 3: Code Review
Explore the codebase:
- `backend/app/agents/` - AI agent logic
- `backend/app/rag/` - RAG pipeline
- `frontend/app/components/` - UI components
- `examples/few_shot/` - Training examples

---

## 📞 Need Help?

If you're stuck, check:
1. **docs/SETUP.md** - Detailed setup instructions
2. **ARCHITECTURE.md** - System architecture
3. **BOB_LOG.md** - Development history

---

**Built with IBM Bob, Granite, and watsonx.ai** 🚀