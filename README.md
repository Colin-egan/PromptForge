# PromptForge

> **Describe it. Edit it. Print it.**
> An AI-powered conversational design tool that turns natural-language descriptions into print-ready, parametric 3D models — and lets you refine them by simply chatting.

Built for the **IBM AI Builders Challenge — July: Reimagine Creative Industries with AI**.

---

## Table of Contents

1. [Selected Challenge Theme](#selected-challenge-theme)
2. [Problem Statement](#problem-statement)
3. [Solution Description](#solution-description)
4. [AI Approach and Architecture](#ai-approach-and-architecture)
5. [How IBM Bob Was Used](#how-ibm-bob-was-used)
6. [Tech Stack](#tech-stack)
7. [Getting Started](#getting-started)
8. [Repository Structure](#repository-structure)
9. [Team](#team)
10. [License](#license)

---

## Selected Challenge Theme

**Reimagine Creative Industries with AI** — specifically the sub-areas of:

- **AI creative partners** — a conversational co-designer for physical objects
- **Creative ideation platforms** — rapid exploration of design variations
- **Personalized creative assistants** — adapts output to the user's printer, materials, and skill level

PromptForge targets one of the fastest-growing creative communities in the world — **makers, hobbyists, educators, tabletop/cosplay creators, and small product designers** — who currently face a steep barrier between *imagination* and *physical artifact*.

---

## Problem Statement

3D printing has democratized physical manufacturing, but **3D modeling has not been democratized alongside it.**

To go from idea to printed object today, a creator must either:

1. **Learn a CAD program** (Fusion 360, OnShape, FreeCAD, Blender) — a 40+ hour learning curve that filters out the vast majority of would-be creators, *or*
2. **Search Thingiverse / Printables / MakerWorld** for someone else's design — limiting creators to remixing what already exists, *or*
3. **Use emerging text-to-3D AI tools** (Shap-E, TripoSR, Meshy) — which produce non-manifold "blob" meshes that are visually interesting but rarely printable without heavy manual cleanup, and which **cannot be precisely edited** ("make the hole 8mm wider" is impossible on a neural mesh).

The result: **the creative bottleneck in 3D printing is no longer the printer — it is the design tool.** Millions of ideas never become objects because the tools require either an engineering background or settle for unprintable, uneditable output.

We need an AI design partner that:
- Understands natural-language descriptions of functional objects
- Produces **print-ready** geometry (manifold, watertight, properly oriented)
- Supports **precise, conversational editing** ("add four M3 mounting holes," "make the wall 2mm thicker")
- Exposes the underlying parameters so creators can iterate visually
- Explains print-readiness in plain language so first-time makers succeed

---

## Solution Description

**PromptForge** is a conversational 3D design assistant that turns plain-English descriptions into parametric, print-ready 3D models — and allows users to refine those models through continued conversation.

### Core User Experience

1. **Describe.** The user types a description in chat:
   > *"I need a desk organizer with three compartments for pens, sticky notes, and paperclips. 12 cm wide, with rounded corners."*

2. **Generate.** PromptForge's AI agent translates the description into [CadQuery](https://cadquery.readthedocs.io) Python code, executes it in a sandboxed environment, and renders the result in an in-browser 3D viewer.

3. **Edit conversationally.** The user can refine the model with follow-up messages:
   > *"Make the middle compartment twice as wide."*
   > *"Add a slot on the side for charging cables."*
   > *"Round the bottom edges more."*

   The agent reads the existing code, applies targeted modifications, and re-renders — *without regenerating from scratch.*

4. **Tune parametrically.** PromptForge automatically extracts the model's variables (height, wall thickness, hole diameter, etc.) and exposes them as **live sliders** that re-render the model in real time.

5. **Verify printability.** A built-in **Print-Readiness Analyzer** checks for thin walls, steep overhangs, trapped volumes, and unprintable features — and explains issues in plain language with suggested fixes.

6. **Export.** The user downloads a print-ready `.stl` file along with a recommended orientation and slicer-setting summary.

### Why This Wins for Creators

| Existing approach | PromptForge |
|---|---|
| Learn CAD (40+ hrs) | Describe in English (30 seconds) |
| Edit a mesh in Blender (hard) | "Make it 20% taller" (instant) |
| Text-to-mesh blobs | True parametric, printable geometry |
| Trial-and-error printing | Pre-flight printability report |
| Fixed Thingiverse downloads | Endless personalization |

### Scope Boundaries (Honest)

PromptForge is optimized for **functional, geometric objects** — organizers, holders, brackets, enclosures, jigs, planters, adaptive aids, simple toys, and parametric props. It is **not** designed for organic shapes, character models, or sculptural work — domains where mesh-based generation is more appropriate and where editability is inherently lossy. This focus is what allows us to guarantee print-ready output and meaningful conversational editing.

---

## AI Approach and Architecture

### Design Philosophy

We made one architectural decision that drives everything else: **code-based parametric geometry, not neural meshes.** The LLM does not generate vertices; it generates **CadQuery Python scripts** that a real CAD kernel (OpenCascade) executes. This guarantees:

- Manifold, watertight, printable output by construction
- True conversational editing (modify variables, re-run)
- Auditable, exportable, version-controllable designs
- Self-correction when geometry fails (errors are fed back to the LLM)

The LLM plays to its strength — **writing code** — instead of being asked to do something it's still bad at (generating clean engineering geometry).

### System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js + React)                   │
│  ┌────────────┐   ┌──────────────────┐   ┌──────────────────┐    │
│  │ Chat panel │   │ 3D viewer (R3F)  │   │ Parameter sliders│    │
│  └─────┬──────┘   └────────▲─────────┘   └────────▲─────────┘    │
└────────┼──────────────────-┼──────────────────────┼──────────────┘
         │                   │                      │
         ▼                   │                      │
┌──────────────────────────────────────────────────────────────────┐
│              Agent Orchestrator (LangChain / LangGraph)          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Intent Router (Granite 3.x on watsonx.ai)                 │  │
│  │   → NEW_MODEL  | EDIT_MODEL  | QUESTION  | EXPORT          │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─────────────────────┐   ┌──────────────────────────────────┐  │
│  │ Code Generator      │   │ Code Editor                      │  │
│  │ (Granite + few-shot)│   │ (reads prior script, diffs it)   │  │
│  └──────────┬──────────┘   └──────────────┬───────────────────┘  │
│             │                              │                     │
│             ▼                              ▼                     │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  RAG: CadQuery API docs + curated design pattern library   │  │
│  │       (Granite embeddings → Milvus / Chroma)               │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│           Sandboxed Execution Service (Python / Docker)          │
│   • Runs CadQuery script in isolated container                   │
│   • Exports STL (download) + GLB (browser preview)               │
│   • Validates: manifold, watertight, bounding box, volume        │
│   • On error → returns traceback to agent for self-correction    │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│              Print-Readiness Analyzer (Granite-powered)          │
│   • Detects: thin walls, overhangs > 45°, trapped volumes        │
│   • Suggests: orientation, supports, infill, material            │
│   • Explains in plain language via Granite                       │
└──────────────────────────────────────────────────────────────────┘
```

### Key AI Components

1. **Intent Router** — A Granite classifier decides whether a user message is a new model request, an edit to the existing model, a question, or an export command. This prevents the system from accidentally regenerating from scratch when the user wanted a tweak.

2. **Code Generator (RAG + few-shot)** — Granite generates CadQuery code using:
   - **Few-shot examples**: 25+ hand-curated `(description → CadQuery script)` pairs across categories (holders, brackets, organizers, enclosures, planters).
   - **RAG retrieval**: Vector-indexed CadQuery API reference and design-pattern snippets, retrieved per request.

3. **Conversational Code Editor** — On edit requests, Granite is given the prior script *and* the user's natural-language change request, and produces a minimal diff. This is what makes editing feel magical instead of destructive.

4. **Self-Correction Loop** — If CadQuery raises an exception (e.g., a failed boolean operation), the traceback is fed back to Granite with up to 3 retry attempts before surfacing an error to the user.

5. **Parameter Extractor** — A lightweight post-processing step extracts top-level numeric variables from the generated script and binds them to UI sliders for real-time re-rendering.

6. **Print-Readiness Analyzer** — Geometric heuristics (wall thickness sampling, overhang angle analysis from mesh normals, trapped-volume detection) generate structured findings, which Granite then translates into a friendly, actionable report.

### Why IBM Granite

- **Strong code generation** for Python (CadQuery is pure Python)
- **Long context windows** support the "read prior script + edit" workflow
- **watsonx.ai governance** provides auditability for what designs the AI produced (important for any future commercial deployment)
- **On-prem / hybrid deployment options** matter for design IP — a clear differentiator vs. cloud-only frontier models

---

## How IBM Bob Was Used

**Documentation**: See [`BOB_LOG.md`](./BOB_LOG.md) for a complete session-by-session log of Bob's contributions, and [`docs/BOB_HIGHLIGHTS.md`](./docs/BOB_HIGHLIGHTS.md) for curated highlights.

IBM Bob served as our **primary development environment** across every phase of the project. Specifically:

### 1. Planning & Architecture
- Used Bob to scope the MVP, break the system into services, and produce the architecture diagram above.
- Bob helped us evaluate the **mesh-vs-parametric** tradeoff early — surfacing risks we would have hit in week 2 if we had chosen mesh generation.

### 2. Scaffolding the Codebase
- Bob generated the initial Next.js + FastAPI project structure, including the Docker sandbox configuration for the CadQuery executor.
- Bob produced boilerplate for the LangChain agent graph, the watsonx.ai client wrapper, and the three.js / React Three Fiber viewer.

### 3. Prompt Engineering for Granite
- We co-authored the system prompts for the Intent Router, Code Generator, and Code Editor with Bob, iterating against a test set of 30 user utterances.
- Bob helped us curate the **few-shot example library** of `(description → CadQuery script)` pairs by generating candidate scripts that we then hand-validated by printing.

### 4. RAG Pipeline Construction
- Bob wrote the ingestion pipeline that chunks and embeds the CadQuery documentation and our internal design-pattern library using Granite embeddings.
- Bob assisted in tuning retrieval (top-k, hybrid keyword + semantic) based on eval results.

### 5. Self-Correction Loop
- Bob designed and implemented the error-feedback loop that catches CadQuery exceptions, formats them as agent observations, and prompts Granite for a corrected script.

### 6. Print-Readiness Analyzer
- Bob helped translate the geometric heuristics (overhang detection from mesh normals, wall-thickness sampling via ray casting) into working Python — a domain neither of our teammates had implemented before.

### 7. Testing & Debugging
- Bob wrote the unit and integration tests for the sandbox executor and the agent graph.
- Bob walked us through several thorny bugs in the CadQuery boolean operations and STL export pipeline.

### 8. Documentation
- This README, the inline code documentation, and the demo video script were all drafted with Bob and edited by the team.

In short: **Bob acted as a sixth team member** — handling boilerplate, pair-programming through tricky integrations, and accelerating decisions on architecture and prompt design.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Primary dev tool | **IBM Bob** |
| LLM | **IBM Granite 3.x** via **watsonx.ai** |
| Agent framework | LangChain / LangGraph |
| Embeddings + Vector store | Granite embeddings + Chroma |
| CAD kernel | CadQuery (OpenCascade) |
| Sandbox | Docker + Python 3.11 |
| Backend API | FastAPI |
| Frontend | Next.js 14, React, TypeScript |
| 3D viewer | React Three Fiber (three.js) |
| Mesh utilities | trimesh, numpy-stl |
| Styling | Tailwind CSS |

---

## Getting Started

### Prerequisites
- Node.js 20+
- Python 3.11+
- Docker
- An IBM watsonx.ai API key and project ID

### Setup

```bash
# Clone the repo
git clone https://github.com/<your-org>/promptforge.git
cd promptforge

# Configure environment
cp .env.example .env
# Fill in: WATSONX_API_KEY, WATSONX_PROJECT_ID, WATSONX_URL

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
docker build -t promptforge-sandbox ./sandbox
uvicorn app.main:app --reload

# Frontend (in a new terminal)
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) and start describing.

### Example Prompts to Try

- *"A wall-mounted holder for my electric toothbrush, with a drainage slot."*
- *"A cable organizer with five channels and screw holes for desk mounting."*
- *"A hexagonal planter, 80mm tall, with a 4mm drainage hole in the bottom."*
- *"Add a lid to it."* (after generating the planter)
- *"Make the walls 30% thicker."*

---

## Repository Structure

```
promptforge/
├── frontend/                 # Next.js app
│   ├── app/
│   ├── components/
│   │   ├── ChatPanel.tsx
│   │   ├── ModelViewer.tsx
│   │   └── ParameterSliders.tsx
│   └── lib/
├── backend/                  # FastAPI + agent
│   ├── app/
│   │   ├── agents/
│   │   │   ├── router.py
│   │   │   ├── generator.py
│   │   │   ├── editor.py
│   │   │   └── analyzer.py
│   │   ├── rag/
│   │   ├── sandbox/          # Docker sandbox for CadQuery
│   │   └── main.py
│   └── tests/
├── examples/                 # Few-shot library + sample STLs
├── docs/                     # Architecture notes
├── .env.example
└── README.md
```

---

## Team

| Name | Role |
|---|---|
| Colin Egan | Project lead |
| _TBD_ | Frontend / 3D viewer |
| _TBD_ | Backend / agent engineering |
| _TBD_ | Prompt + RAG engineering |
| _TBD_ | Design + demo production |

---

## Acknowledgements

- **IBM** for the AI Builders Challenge, Bob, Granite, and watsonx.ai
- **CadQuery** maintainers for an outstanding open-source CAD kernel
- The maker, cosplay, and tabletop communities — for whom this is built

---

## License

MIT — see [LICENSE](./LICENSE).