# PromptForge API Reference

Complete reference for the PromptForge REST API.

## Base URL

```
http://localhost:8000/api
```

## Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
   - [Health Check](#health-check)
   - [Chat](#chat)
   - [Generate Model](#generate-model)
   - [Edit Model](#edit-model)
   - [Update Parameters](#update-parameters)
   - [Analyze Model](#analyze-model)
   - [Export Model](#export-model)
   - [Get Model](#get-model)
3. [Data Models](#data-models)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)

---

## Authentication

Currently, the API does not require authentication. This may change in production deployments.

---

## Endpoints

### Health Check

Check the status of all system components.

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "api": "healthy",
    "sandbox": "healthy",
    "watsonx": "healthy",
    "chromadb": "healthy"
  }
}
```

**Status Codes:**
- `200 OK` - All services healthy
- `503 Service Unavailable` - One or more services unhealthy

---

### Chat

Conversational interface for model generation and editing.

**Endpoint:** `POST /api/chat`

**Request Body:**
```json
{
  "message": "Create a phone stand 80mm wide",
  "history": [
    {
      "role": "user",
      "content": "Previous message",
      "model_id": "optional-model-id"
    },
    {
      "role": "assistant",
      "content": "Previous response"
    }
  ]
}
```

**Parameters:**
- `message` (string, required): User's message
- `history` (array, optional): Conversation history for context

**Response:**
```json
{
  "response": "I've created a phone stand for you...",
  "intent": "NEW_MODEL",
  "model_id": "abc123",
  "model_url": "/api/models/abc123.stl",
  "parameters": [
    {
      "name": "width",
      "value": 80.0,
      "min": 40.0,
      "max": 160.0,
      "step": 5.0,
      "label": "Width (mm)",
      "category": "dimensions"
    }
  ]
}
```

**Intent Types:**
- `NEW_MODEL` - Generate a new model
- `EDIT` - Edit existing model
- `QUESTION` - Answer a question
- `EXPORT` - Export model in specific format

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid request
- `500 Internal Server Error` - Generation failed

---

### Generate Model

Direct model generation without conversation.

**Endpoint:** `POST /api/generate`

**Request Body:**
```json
{
  "description": "A simple box 50mm on each side"
}
```

**Parameters:**
- `description` (string, required): Description of the model to generate

**Response:**
```json
{
  "success": true,
  "model_id": "abc123",
  "model_url": "/api/models/abc123.stl",
  "code": "import cadquery as cq\n...",
  "parameters": [...],
  "message": "Model generated successfully"
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid description
- `500 Internal Server Error` - Generation failed

---

### Edit Model

Edit an existing model with natural language instructions.

**Endpoint:** `POST /api/edit`

**Request Body:**
```json
{
  "model_id": "abc123",
  "instruction": "Make it 20mm taller"
}
```

**Parameters:**
- `model_id` (string, required): ID of the model to edit
- `instruction` (string, required): Edit instruction

**Response:**
```json
{
  "success": true,
  "new_model_id": "def456",
  "model_url": "/api/models/def456.stl",
  "changes": "Increased height from 50mm to 70mm",
  "code": "import cadquery as cq\n..."
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid model ID or instruction
- `404 Not Found` - Model not found
- `500 Internal Server Error` - Edit failed

---

### Update Parameters

Update model parameters and regenerate.

**Endpoint:** `POST /api/parameters`

**Request Body:**
```json
{
  "model_id": "abc123",
  "parameters": {
    "width": 100.0,
    "height": 75.0,
    "depth": 50.0
  }
}
```

**Parameters:**
- `model_id` (string, required): ID of the model
- `parameters` (object, required): Key-value pairs of parameter names and new values

**Response:**
```json
{
  "success": true,
  "new_model_id": "ghi789",
  "model_url": "/api/models/ghi789.stl"
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid parameters
- `404 Not Found` - Model not found
- `500 Internal Server Error` - Update failed

---

### Analyze Model

Analyze a model for 3D print-readiness.

**Endpoint:** `POST /api/analyze`

**Request Body:**
```json
{
  "model_id": "abc123"
}
```

**Parameters:**
- `model_id` (string, required): ID of the model to analyze

**Response:**
```json
{
  "printable": true,
  "status": "ready",
  "issues": [
    {
      "type": "overhang",
      "severity": "warning",
      "message": "Some faces have overhangs > 45°",
      "details": "3 faces require supports"
    }
  ],
  "recommendations": [
    "Add supports for overhanging features",
    "Use 20% infill for good strength",
    "Recommended layer height: 0.2mm"
  ],
  "metadata": {
    "dimensions": {
      "width": 80.0,
      "height": 120.0,
      "depth": 50.0
    },
    "volume": 480000.0,
    "surface_area": 35200.0
  },
  "report": "✅ **Print-Ready**\n\nYour model looks good..."
}
```

**Issue Severities:**
- `critical` - Must fix before printing
- `warning` - Should address for best results
- `info` - Optional improvements

**Status Values:**
- `ready` - No critical issues
- `needs_attention` - Has warnings
- `not_printable` - Has critical issues

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Model not found
- `500 Internal Server Error` - Analysis failed

---

### Export Model

Export a model in a specific format.

**Endpoint:** `GET /api/export/{model_id}/{format}`

**Path Parameters:**
- `model_id` (string, required): ID of the model
- `format` (string, required): Export format (`stl`, `step`, or `glb`)

**Response:**
- Binary file download with appropriate Content-Type header

**Content-Types:**
- `stl` → `application/sla` or `model/stl`
- `step` → `application/step`
- `glb` → `model/gltf-binary`

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Model not found
- `400 Bad Request` - Invalid format
- `500 Internal Server Error` - Export failed

---

### Get Model

Retrieve a model file (STL format).

**Endpoint:** `GET /api/models/{model_id}.stl`

**Path Parameters:**
- `model_id` (string, required): ID of the model

**Response:**
- Binary STL file with `Content-Type: application/sla`

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - Model not found

---

## Data Models

### Parameter

```typescript
interface Parameter {
  name: string;           // Parameter name (e.g., "width")
  value: number;          // Current value
  min: number;            // Minimum allowed value
  max: number;            // Maximum allowed value
  step: number;           // Increment step
  label: string;          // User-friendly label (e.g., "Width (mm)")
  category: string;       // Category (dimensions, structure, features, angles, counts)
}
```

### ChatMessage

```typescript
interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  model_id?: string;      // Optional model ID for context
}
```

### AnalysisIssue

```typescript
interface AnalysisIssue {
  type: string;           // Issue type (e.g., "thin_walls", "overhang")
  severity: "critical" | "warning" | "info";
  message: string;        // Human-readable message
  details?: string;       // Additional details
}
```

### ModelMetadata

```typescript
interface ModelMetadata {
  dimensions: {
    width: number;
    height: number;
    depth: number;
  };
  volume: number;         // Volume in mm³
  surface_area: number;   // Surface area in mm²
  bounding_box?: {
    min: [number, number, number];
    max: [number, number, number];
  };
}
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong",
  "error_code": "GENERATION_FAILED",
  "timestamp": "2026-06-09T20:00:00Z"
}
```

### Common Error Codes

- `INVALID_REQUEST` - Malformed request body
- `MODEL_NOT_FOUND` - Requested model doesn't exist
- `GENERATION_FAILED` - Code generation failed
- `EXECUTION_FAILED` - Code execution failed
- `ANALYSIS_FAILED` - Print analysis failed
- `EXPORT_FAILED` - Model export failed
- `SERVICE_UNAVAILABLE` - Required service is down

### HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

---

## Rate Limiting

Currently, no rate limiting is enforced. In production:

- **Rate Limit**: 100 requests per minute per IP
- **Burst Limit**: 10 concurrent requests
- **Headers**:
  - `X-RateLimit-Limit`: Total requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Time when limit resets

---

## Examples

### Example 1: Generate and Analyze

```bash
# Generate a model
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"description": "A simple box 50mm on each side"}'

# Response: {"success": true, "model_id": "abc123", ...}

# Analyze the model
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"model_id": "abc123"}'

# Download STL
curl -O http://localhost:8000/api/models/abc123.stl
```

### Example 2: Conversational Workflow

```bash
# Initial generation
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a phone stand",
    "history": []
  }'

# Edit the model
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Make it wider",
    "history": [
      {"role": "user", "content": "Create a phone stand", "model_id": "abc123"},
      {"role": "assistant", "content": "Created a phone stand"}
    ]
  }'
```

### Example 3: Parameter Adjustment

```bash
# Update parameters
curl -X POST http://localhost:8000/api/parameters \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "abc123",
    "parameters": {
      "width": 100.0,
      "height": 75.0
    }
  }'
```

---

## WebSocket Support (Future)

Real-time updates for long-running operations:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/generate');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress:', data.progress);
};

ws.send(JSON.stringify({
  action: 'generate',
  description: 'A complex model'
}));
```

---

## SDK Support (Future)

Official SDKs planned for:
- Python
- JavaScript/TypeScript
- Go

Example Python SDK usage:
```python
from promptforge import PromptForge

client = PromptForge(api_url="http://localhost:8000")

# Generate a model
model = client.generate("Create a phone stand")
print(f"Model ID: {model.id}")

# Analyze
analysis = client.analyze(model.id)
print(f"Printable: {analysis.printable}")

# Export
model.export("phone_stand.stl", format="stl")
```

---

## Changelog

### v1.0.0 (Current)
- Initial API release
- Chat, generate, edit, analyze, export endpoints
- Parameter extraction and updates
- Print-readiness analysis

### Planned Features
- WebSocket support for real-time updates
- Batch operations
- Model versioning and history
- User accounts and saved models
- Rate limiting and authentication
- Official SDKs

---

For more information, see:
- [User Guide](USER_GUIDE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [Architecture Documentation](ARCHITECTURE.md)