# PromptForge Developer Guide

> **A comprehensive guide for developers contributing to PromptForge**

This guide covers the architecture, development workflow, testing strategies, and best practices for working on PromptForge.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Development Environment Setup](#development-environment-setup)
3. [Project Structure](#project-structure)
4. [Core Components](#core-components)
5. [Development Workflow](#development-workflow)
6. [Testing Strategy](#testing-strategy)
7. [Code Style & Standards](#code-style--standards)
8. [Debugging Guide](#debugging-guide)
9. [Performance Optimization](#performance-optimization)
10. [Deployment](#deployment)
11. [Contributing Guidelines](#contributing-guidelines)

---

## Architecture Overview

### Design Philosophy

PromptForge uses **code-based parametric geometry** instead of neural mesh generation. This architectural decision drives everything else:

- **LLM generates CadQuery Python scripts**, not vertices
- **CAD kernel (OpenCascade) executes** the scripts
- **Guarantees**: Manifold, watertight, printable output by construction
- **Enables**: True conversational editing, auditability, version control

### System Layers

```
┌─────────────────────────────────────────────────────────────┐
│ Frontend Layer (Next.js + React + TypeScript)              │
│  • Chat interface for natural language input               │
│  • 3D viewer (React Three Fiber) for real-time preview     │
│  • Parameter sliders for interactive tuning                │
│  • Analysis report display                                 │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│ API Layer (FastAPI + Pydantic)                             │
│  • Request routing and validation                          │
│  • Session management                                      │
│  • Error handling and logging                              │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│ Agent Orchestration (LangChain/LangGraph)                  │
│  • Intent Router: Classify user requests                   │
│  • Code Generator: Create new CadQuery scripts             │
│  • Code Editor: Modify existing scripts                    │
│  • Parameter Extractor: Extract tunable variables          │
│  • Print Analyzer: Check printability                      │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│ Knowledge Layer (RAG + Vector DB)                          │
│  • Chroma vector database                                  │
│  • CadQuery API documentation                              │
│  • Few-shot example library (25+ examples)                 │
│  • Granite embeddings                                      │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│ Execution Layer (Docker Sandbox)                           │
│  • Isolated CadQuery execution                             │
│  • STL/GLB export                                          │
│  • Geometry validation                                     │
│  • Error capture and reporting                             │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│ AI Services (IBM watsonx.ai + Granite 3.x)                 │
│  • Code generation                                         │
│  • Intent classification                                   │
│  • Report generation                                       │
│  • Embeddings                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Development Environment Setup

### Prerequisites

- **Node.js**: 20+ (for frontend)
- **Python**: 3.11+ (for backend)
- **Docker**: Latest stable (for sandbox)
- **Git**: For version control
- **IBM watsonx.ai**: API key and project ID

### Initial Setup

```bash
# 1. Clone the repository
git clone https://github.com/<your-org>/promptforge.git
cd promptforge

# 2. Configure environment variables
cp .env.example .env
# Edit .env and add:
#   WATSONX_API_KEY=your_api_key_here
#   WATSONX_PROJECT_ID=your_project_id_here
#   WATSONX_URL=https://us-south.ml.cloud.ibm.com

# 3. Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 4. Build Docker sandbox
docker build -t promptforge-sandbox ./sandbox

# 5. Initialize RAG database (one-time)
python -m app.scripts.ingest

# 6. Frontend setup (in new terminal)
cd frontend
npm install

# 7. Verify setup
cd backend && pytest
cd frontend && npm run build
```

### IDE Configuration

#### VS Code (Recommended)

Install extensions:
- Python (Microsoft)
- Pylance
- ESLint
- Prettier
- TypeScript and JavaScript Language Features

Workspace settings (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

---

## Project Structure

```
promptforge/
├── backend/                      # Python backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── watsonx_client.py    # IBM watsonx.ai client wrapper
│   │   ├── sandbox_manager.py   # Docker sandbox orchestration
│   │   ├── agents/              # AI agent implementations
│   │   │   ├── __init__.py
│   │   │   ├── router.py        # Intent classification
│   │   │   ├── generator.py     # Code generation
│   │   │   ├── editor.py        # Code editing
│   │   │   ├── analyzer.py      # Print-readiness analysis
│   │   │   ├── parameter_extractor.py  # Parameter extraction
│   │   │   └── prompts.py       # System prompts
│   │   ├── rag/                 # RAG pipeline
│   │   │   ├── __init__.py
│   │   │   ├── chroma_client.py # Vector DB client
│   │   │   ├── ingestion.py     # Document ingestion
│   │   │   └── retrieval.py     # Context retrieval
│   │   └── scripts/             # Utility scripts
│   │       └── ingest.py        # RAG database initialization
│   ├── sandbox/                 # Docker sandbox
│   │   ├── Dockerfile
│   │   └── executor.py          # CadQuery execution script
│   ├── tests/                   # Test suite
│   │   ├── __init__.py
│   │   ├── test_watsonx_client.py
│   │   ├── test_integration.py
│   │   └── README.md
│   ├── data/                    # Persistent data
│   │   └── chroma/              # Vector database storage
│   ├── requirements.txt         # Python dependencies
│   ├── pytest.ini              # Pytest configuration
│   └── Dockerfile              # Backend container
├── frontend/                    # Next.js frontend
│   ├── app/
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Main page
│   │   ├── globals.css         # Global styles
│   │   ├── components/         # React components
│   │   │   ├── ChatPanel.tsx   # Chat interface
│   │   │   ├── ModelViewer.tsx # 3D viewer
│   │   │   ├── ParameterSliders.tsx  # Parameter controls
│   │   │   └── AnalysisReport.tsx    # Print analysis display
│   │   └── lib/
│   │       └── api.ts          # API client
│   ├── public/                 # Static assets
│   ├── package.json            # Node dependencies
│   ├── tsconfig.json           # TypeScript config
│   ├── tailwind.config.ts      # Tailwind CSS config
│   └── next.config.js          # Next.js config
├── examples/                    # Few-shot example library
│   ├── few_shot/
│   │   ├── holders/            # Phone stands, pen holders, etc.
│   │   ├── organizers/         # Desk organizers, cable management
│   │   ├── brackets/           # Mounting brackets, supports
│   │   ├── enclosures/         # Electronics cases, battery holders
│   │   ├── planters/           # Plant pots, hanging planters
│   │   └── functional/         # Hooks, clips, adapters
│   └── validate_examples.py    # Example validation script
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md         # System architecture
│   ├── API_REFERENCE.md        # API documentation
│   ├── USER_GUIDE.md           # User guide
│   ├── DEVELOPER_GUIDE.md      # This file
│   └── SETUP.md                # Setup instructions
├── .env.example                # Environment template
├── .gitignore
├── docker-compose.yml          # Multi-container orchestration
├── README.md                   # Project overview
└── BOB_LOG.md                  # Development log
```

---

## Core Components

### 1. FastAPI Backend (`backend/app/main.py`)

**Purpose**: HTTP API server that orchestrates all backend services.

**Key Endpoints**:
```python
POST   /api/chat              # Main conversational interface
POST   /api/generate          # Direct model generation
POST   /api/edit              # Edit existing model
POST   /api/parameters        # Update parameter values
POST   /api/analyze           # Print-readiness analysis
GET    /api/export/{model_id}/{format}  # Download STL/GLB
GET    /api/models/{model_id}.stl       # Retrieve model
GET    /api/health            # Health check
```

**Request Flow**:
1. Request validation (Pydantic models)
2. Intent classification (Router agent)
3. Agent execution (Generator/Editor/Analyzer)
4. Response formatting
5. Error handling

**Example**:
```python
@app.post("/api/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    # Classify intent
    intent = await router_agent.classify(request.message)
    
    # Route to appropriate agent
    if intent == "NEW_MODEL":
        result = await generator_agent.generate(request.message)
    elif intent == "EDIT_MODEL":
        result = await editor_agent.edit(request.message, request.current_code)
    
    return ChatResponse(
        message=result.message,
        model_data=result.model_data,
        parameters=result.parameters
    )
```

### 2. IBM watsonx.ai Client (`backend/app/watsonx_client.py`)

**Purpose**: Wrapper around IBM watsonx.ai SDK for Granite model access.

**Key Methods**:
```python
class WatsonxClient:
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Granite model"""
        
    def generate_with_schema(self, prompt: str, schema: dict) -> dict:
        """Generate structured JSON output"""
        
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for RAG"""
```

**Configuration**:
```python
granite_config = {
    "model_id": "ibm/granite-3-8b-instruct",
    "parameters": {
        "temperature": 0.2,      # Low for code generation
        "max_tokens": 2048,
        "top_p": 0.95,
        "stop_sequences": ["```"]
    }
}
```

### 3. Agent System (`backend/app/agents/`)

#### Intent Router (`router.py`)

**Purpose**: Classify user messages into actionable intents.

**Intents**:
- `NEW_MODEL`: Create new design
- `EDIT_MODEL`: Modify existing design
- `ADJUST_PARAMETERS`: Change parameter values
- `ANALYZE`: Check printability
- `QUESTION`: Answer query
- `EXPORT`: Download model

**Implementation**:
```python
class IntentRouter:
    async def classify(self, message: str, context: dict) -> Intent:
        prompt = self._build_classification_prompt(message, context)
        response = await self.watsonx.generate_with_schema(
            prompt, 
            schema=INTENT_SCHEMA
        )
        return Intent(**response)
```

#### Code Generator (`generator.py`)

**Purpose**: Generate CadQuery Python code from natural language.

**Process**:
1. Retrieve relevant few-shot examples (top-5)
2. Retrieve CadQuery API docs (top-10)
3. Construct prompt with examples + docs
4. Generate code with Granite
5. Validate syntax
6. Execute in sandbox
7. Self-correct if errors (up to 3 attempts)

**Prompt Structure**:
```python
SYSTEM_PROMPT = """You are an expert CadQuery programmer.
Generate clean, printable 3D models using CadQuery.

Guidelines:
- Use clear variable names
- Add comments for complex operations
- Ensure manifold geometry
- Consider printability (overhangs, supports)
"""

def build_prompt(description: str, examples: List[str], docs: str) -> str:
    return f"""
{SYSTEM_PROMPT}

Examples:
{examples}

API Reference:
{docs}

User Request: {description}

Generate CadQuery code:
"""
```

#### Code Editor (`editor.py`)

**Purpose**: Modify existing CadQuery code based on natural language edits.

**Key Challenge**: Preserve structure while making targeted changes.

**Process**:
1. Parse current code (AST analysis)
2. Identify modification targets
3. Generate minimal diff
4. Validate changes
5. Execute updated code

**Example**:
```python
async def edit(self, current_code: str, edit_request: str) -> EditResult:
    # Analyze current code
    structure = self._analyze_code(current_code)
    
    # Generate edit prompt
    prompt = self._build_edit_prompt(current_code, edit_request, structure)
    
    # Generate modified code
    new_code = await self.watsonx.generate(prompt)
    
    # Validate and execute
    result = await self.sandbox.execute(new_code)
    
    return EditResult(code=new_code, model=result.model)
```

#### Parameter Extractor (`parameter_extractor.py`)

**Purpose**: Extract tunable parameters from generated code.

**Process**:
1. Parse Python AST
2. Identify numeric assignments
3. Infer min/max ranges
4. Generate UI metadata

**Output Format**:
```python
{
    "name": "height",
    "label": "Height (mm)",
    "value": 80,
    "min": 20,
    "max": 200,
    "step": 1,
    "type": "float"
}
```

#### Print Analyzer (`analyzer.py`)

**Purpose**: Check model printability and generate reports.

**Checks**:
- Wall thickness (ray casting)
- Overhangs > 45° (normal analysis)
- Trapped volumes (topology)
- Manifold validation
- Dimensional checks

**Report Generation**:
```python
async def analyze(self, stl_path: str) -> AnalysisReport:
    # Geometric analysis
    findings = self._analyze_geometry(stl_path)
    
    # Generate plain-language report with Granite
    prompt = self._build_report_prompt(findings)
    report = await self.watsonx.generate(prompt)
    
    return AnalysisReport(
        findings=findings,
        report=report,
        printable=findings.is_printable
    )
```

### 4. RAG Pipeline (`backend/app/rag/`)

#### Ingestion (`ingestion.py`)

**Purpose**: Process and index documentation for retrieval.

**Process**:
1. Load documents (CadQuery docs, examples)
2. Chunk text (500 tokens, 50 overlap)
3. Generate embeddings (Granite)
4. Store in Chroma vector DB

**Usage**:
```bash
python -m app.scripts.ingest
```

#### Retrieval (`retrieval.py`)

**Purpose**: Retrieve relevant context for code generation.

**Methods**:
- **Semantic search**: Vector similarity (Granite embeddings)
- **Keyword search**: BM25 for exact matches
- **Hybrid**: Combine both with weighted scoring

**Example**:
```python
async def retrieve(self, query: str, top_k: int = 10) -> List[Document]:
    # Generate query embedding
    query_embedding = await self.watsonx.embed([query])
    
    # Semantic search
    semantic_results = self.chroma.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )
    
    # Keyword search
    keyword_results = self.bm25.search(query, top_k)
    
    # Combine and re-rank
    return self._hybrid_rank(semantic_results, keyword_results)
```

### 5. Docker Sandbox (`backend/sandbox/`)

**Purpose**: Isolated execution of untrusted CadQuery code.

**Security**:
- No network access
- Read-only filesystem (except `/output`)
- CPU/memory limits
- 30-second timeout
- Limited system calls

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

# Install CadQuery and dependencies
RUN pip install cadquery cadquery-ocp trimesh numpy-stl

# Copy executor script
COPY executor.py /app/
WORKDIR /app

# Run as non-root user
RUN useradd -m sandbox
USER sandbox

CMD ["python", "executor.py"]
```

**Executor** (`executor.py`):
```python
def execute_code(code: str) -> dict:
    try:
        # Execute CadQuery code
        exec_globals = {}
        exec(code, exec_globals)
        
        # Export STL and GLB
        result = exec_globals.get('result')
        result.val().exportStl('/output/model.stl')
        
        return {
            "success": True,
            "stl_path": "/output/model.stl"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
```

### 6. Frontend Components (`frontend/app/components/`)

#### ChatPanel (`ChatPanel.tsx`)

**Purpose**: Conversational interface for user input.

**Features**:
- Message history
- Markdown rendering
- Code syntax highlighting
- Loading states
- Error display

**Key State**:
```typescript
interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const [messages, setMessages] = useState<Message[]>([]);
const [input, setInput] = useState('');
const [isLoading, setIsLoading] = useState(false);
```

#### ModelViewer (`ModelViewer.tsx`)

**Purpose**: 3D visualization using React Three Fiber.

**Features**:
- Orbit controls
- Grid helper
- Lighting
- STL/GLB loading
- Screenshot export

**Implementation**:
```typescript
<Canvas camera={{ position: [100, 100, 100] }}>
  <ambientLight intensity={0.5} />
  <directionalLight position={[10, 10, 5]} />
  <OrbitControls />
  <STLModel url={modelUrl} />
  <gridHelper args={[200, 20]} />
</Canvas>
```

#### ParameterSliders (`ParameterSliders.tsx`)

**Purpose**: Interactive parameter controls.

**Features**:
- Dynamic slider generation
- Real-time updates
- Value display
- Reset to defaults

**Example**:
```typescript
interface Parameter {
  name: string;
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
}

const handleChange = async (name: string, value: number) => {
  const response = await api.updateParameters({
    [name]: value
  });
  setModelUrl(response.model_url);
};
```

---

## Development Workflow

### 1. Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes
# ... edit files ...

# 3. Run tests
cd backend && pytest
cd frontend && npm test

# 4. Format code
black backend/app
prettier --write frontend/app

# 5. Commit changes
git add .
git commit -m "feat: add your feature description"

# 6. Push and create PR
git push origin feature/your-feature-name
```

### 2. Adding a New Agent

1. **Create agent file**: `backend/app/agents/your_agent.py`
2. **Define agent class**:
```python
from app.watsonx_client import WatsonxClient

class YourAgent:
    def __init__(self, watsonx: WatsonxClient):
        self.watsonx = watsonx
    
    async def process(self, input_data: dict) -> dict:
        # Agent logic here
        pass
```
3. **Add system prompt**: `backend/app/agents/prompts.py`
4. **Write tests**: `backend/tests/test_your_agent.py`
5. **Integrate into main**: `backend/app/main.py`

### 3. Adding Few-Shot Examples

1. **Create example file**: `examples/few_shot/category/example_name.json`
```json
{
  "id": "example_name",
  "category": "category",
  "description": "Natural language description",
  "code": "import cadquery as cq\n...",
  "parameters": ["height", "width", "thickness"],
  "print_notes": "Print upright, no supports needed",
  "validated": true
}
```
2. **Validate example**:
```bash
python examples/validate_examples.py examples/few_shot/category/example_name.json
```
3. **Re-ingest RAG database**:
```bash
python -m app.scripts.ingest
```

### 4. Updating Documentation

- **Code changes**: Update inline docstrings
- **API changes**: Update `docs/API_REFERENCE.md`
- **Architecture changes**: Update `ARCHITECTURE.md`
- **User-facing changes**: Update `docs/USER_GUIDE.md`

---

## Testing Strategy

### Backend Tests

**Unit Tests** (`backend/tests/`):
```python
# test_watsonx_client.py
def test_generate():
    client = WatsonxClient()
    result = client.generate("Test prompt")
    assert isinstance(result, str)
    assert len(result) > 0

# test_parameter_extractor.py
def test_extract_parameters():
    code = "height = 80\nwidth = 50"
    params = extract_parameters(code)
    assert len(params) == 2
    assert params[0]["name"] == "height"
```

**Integration Tests** (`backend/tests/test_integration.py`):
```python
@pytest.mark.asyncio
async def test_end_to_end_generation():
    # Test full pipeline
    response = await client.post("/api/chat", json={
        "message": "Create a phone holder"
    })
    assert response.status_code == 200
    assert "model_url" in response.json()
```

**Run Tests**:
```bash
cd backend
pytest                    # All tests
pytest -v                 # Verbose
pytest -k test_generate   # Specific test
pytest --cov=app          # With coverage
```

### Frontend Tests

**Component Tests** (`frontend/app/components/__tests__/`):
```typescript
import { render, screen } from '@testing-library/react';
import ChatPanel from '../ChatPanel';

test('renders chat input', () => {
  render(<ChatPanel />);
  const input = screen.getByPlaceholderText(/describe/i);
  expect(input).toBeInTheDocument();
});
```

**Run Tests**:
```bash
cd frontend
npm test                  # All tests
npm test -- --coverage    # With coverage
```

### Manual Testing Checklist

- [ ] New model generation works
- [ ] Conversational editing preserves context
- [ ] Parameter sliders update model in real-time
- [ ] Print analysis detects issues
- [ ] Export downloads correct file format
- [ ] Error messages are user-friendly
- [ ] 3D viewer renders correctly
- [ ] Mobile responsive design works

---

## Code Style & Standards

### Python (Backend)

**Style Guide**: PEP 8 + Black formatter

**Key Conventions**:
```python
# Imports: stdlib, third-party, local
import os
from typing import List, Dict

from fastapi import FastAPI
from pydantic import BaseModel

from app.watsonx_client import WatsonxClient

# Type hints everywhere
async def generate_code(prompt: str, context: Dict[str, Any]) -> str:
    """Generate CadQuery code from prompt.
    
    Args:
        prompt: Natural language description
        context: Additional context (examples, docs)
    
    Returns:
        Generated CadQuery Python code
    
    Raises:
        GenerationError: If code generation fails
    """
    pass

# Constants in UPPER_CASE
MAX_RETRIES = 3
DEFAULT_TEMPERATURE = 0.2

# Classes in PascalCase
class CodeGenerator:
    pass

# Functions/variables in snake_case
def extract_parameters(code: str) -> List[Parameter]:
    pass
```

**Linting**:
```bash
pylint backend/app
mypy backend/app
black backend/app --check
```

### TypeScript (Frontend)

**Style Guide**: Airbnb + Prettier

**Key Conventions**:
```typescript
// Interfaces in PascalCase
interface ModelData {
  id: string;
  url: string;
  parameters: Parameter[];
}

// Components in PascalCase
export default function ChatPanel({ onSubmit }: ChatPanelProps) {
  // Hooks at top
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  
  // Event handlers with 'handle' prefix
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await onSubmit(input);
  };
  
  return (
    <div className="chat-panel">
      {/* JSX */}
    </div>
  );
}

// Constants in UPPER_CASE
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

// Functions in camelCase
function formatTimestamp(date: Date): string {
  return date.toLocaleString();
}
```

**Linting**:
```bash
npm run lint
npm run type-check
```

---

## Debugging Guide

### Backend Debugging

**Enable Debug Logging**:
```python
# backend/app/main.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Common Issues**:

1. **watsonx.ai Connection Errors**:
```bash
# Check credentials
echo $WATSONX_API_KEY
echo $WATSONX_PROJECT_ID

# Test connection
python -c "from app.watsonx_client import WatsonxClient; client = WatsonxClient(); print(client.generate('test'))"
```

2. **Sandbox Execution Failures**:
```bash
# Check Docker
docker ps
docker logs <container_id>

# Test sandbox directly
docker run -it promptforge-sandbox python executor.py
```

3. **RAG Retrieval Issues**:
```bash
# Check Chroma database
python -c "from app.rag.chroma_client import ChromaClient; client = ChromaClient(); print(client.collection.count())"

# Re-ingest if needed
python -m app.scripts.ingest
```

### Frontend Debugging

**Browser DevTools**:
- Console: Check for JavaScript errors
- Network: Inspect API requests/responses
- React DevTools: Inspect component state

**Common Issues**:

1. **API Connection Errors**:
```typescript
// Check API URL
console.log(process.env.NEXT_PUBLIC_API_URL);

// Test endpoint
fetch('http://localhost:8000/api/health')
  .then(r => r.json())
  .then(console.log);
```

2. **3D Viewer Not Rendering**:
```typescript
// Check model URL
console.log(modelUrl);

// Check Three.js errors
<Canvas onError={(error) => console.error('Three.js error:', error)}>
```

---

## Performance Optimization

### Backend Optimization

1. **Async Operations**:
```python
# Use async/await for I/O operations
async def generate_model(prompt: str):
    # Parallel RAG retrieval
    examples, docs = await asyncio.gather(
        retrieve_examples(prompt),
        retrieve_docs(prompt)
    )
```

2. **Caching**:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_embeddings(text: str) -> List[float]:
    return watsonx.embed([text])[0]
```

3. **Connection Pooling**:
```python
# Reuse watsonx client
app.state.watsonx = WatsonxClient()

@app.get("/api/generate")
async def generate(request: Request):
    client = request.app.state.watsonx
```

### Frontend Optimization

1. **Code Splitting**:
```typescript
// Lazy load 3D viewer
const ModelViewer = dynamic(() => import('./ModelViewer'), {
  ssr: false,
  loading: () => <LoadingSpinner />
});
```

2. **Debouncing**:
```typescript
// Debounce parameter updates
const debouncedUpdate = useMemo(
  () => debounce((params) => updateModel(params), 500),
  []
);
```

3. **Memoization**:
```typescript
// Memoize expensive computations
const processedMessages = useMemo(
  () => messages.map(processMessage),
  [messages]
);
```

---

## Deployment

### Development Deployment

```bash
# Start all services
docker-compose up

# Or manually:
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Production Deployment

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose logs -f
```

### Environment Variables

**Required**:
- `WATSONX_API_KEY`: IBM watsonx.ai API key
- `WATSONX_PROJECT_ID`: watsonx.ai project ID
- `WATSONX_URL`: watsonx.ai endpoint URL

**Optional**:
- `LOG_LEVEL`: Logging level (default: INFO)
- `MAX_RETRIES`: Max self-correction attempts (default: 3)
- `SANDBOX_TIMEOUT`: Sandbox execution timeout (default: 30s)

---

## Contributing Guidelines

### Pull Request Process

1. **Fork and branch**: Create feature branch from `main`
2. **Implement**: Make changes with tests
3. **Test**: Run full test suite
4. **Document**: Update relevant docs
5. **Commit**: Use conventional commits
6. **PR**: Create pull request with description
7. **Review**: Address review comments
8. **Merge**: Squash and merge when approved

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples**:
```
feat(agents): add self-correction loop to code generator

Implements retry logic with error feedback to Granite.
Includes up to 3 attempts before surfacing error to user.

Closes #42
```

### Code Review Checklist

- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Performance impact considered
- [ ] Security implications reviewed

---

## Additional Resources

- **Architecture**: See `ARCHITECTURE.md` for system design
- **API Reference**: See `docs/API_REFERENCE.md` for endpoint docs
- **User Guide**: See `docs/USER_GUIDE.md` for user-facing docs
- **Setup Guide**: See `docs/SETUP.md` for detailed setup
- **CadQuery Docs**: https://cadquery.readthedocs.io
- **IBM watsonx.ai**: https://www.ibm.com/watsonx

---

## Getting Help

- **Issues**: Open GitHub issue with bug/feature template
- **Discussions**: Use GitHub Discussions for questions
- **Slack**: Join #promptforge channel (if applicable)
- **Email**: contact@promptforge.dev

---

**Happy coding! 🚀**