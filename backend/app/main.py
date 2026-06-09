"""
PromptForge Backend - FastAPI Application
"""
import io
import uuid
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from app.sandbox_manager import get_sandbox_manager, SandboxExecutionError
from app.watsonx_client import get_watsonx_client, GenerationParams
from app.agents.analyzer import GeometricAnalyzer, AnalysisResult
from app.agents.prompts import build_analysis_report_prompt

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PromptForge API",
    description="AI-powered conversational 3D design tool",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# In-memory model store  {model_id -> ModelRecord}
# ============================================================================

class ModelRecord:
    def __init__(
        self,
        model_id: str,
        description: str,
        code: str,
        stl_bytes: Optional[bytes],
        step_bytes: Optional[bytes],
        glb_bytes: Optional[bytes],
        metadata: Optional[dict],
        attempts: int,
    ):
        self.model_id = model_id
        self.description = description
        self.code = code
        self.stl_bytes = stl_bytes
        self.step_bytes = step_bytes
        self.glb_bytes = glb_bytes
        self.metadata = metadata
        self.attempts = attempts
        self.created_at = datetime.utcnow().isoformat()


_model_store: Dict[str, ModelRecord] = {}


def _stl_to_glb(stl_bytes: bytes) -> Optional[bytes]:
    """Convert STL bytes to GLB using trimesh."""
    try:
        import trimesh
        mesh = trimesh.load(io.BytesIO(stl_bytes), file_type="stl")
        glb_io = io.BytesIO()
        mesh.export(glb_io, file_type="glb")
        return glb_io.getvalue()
    except Exception as e:
        logger.warning(f"GLB conversion failed: {e}")
        return None


# ============================================================================
# Request/Response Models
# ============================================================================

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    services: Dict[str, str]


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None)
    model_id: Optional[str] = Field(None, description="Current model ID if editing")


class ChatResponse(BaseModel):
    message: str
    intent: str
    model_id: Optional[str] = None
    code: Optional[str] = None
    model_url: Optional[str] = None
    parameters: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class GenerateRequest(BaseModel):
    description: str = Field(..., description="Natural language description")
    parameters: Optional[Dict[str, Any]] = Field(None)


class GenerateResponse(BaseModel):
    success: bool
    model_id: str
    code: str
    model_url: Optional[str] = None
    parameters: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class EditRequest(BaseModel):
    model_id: str
    instruction: str


class EditResponse(BaseModel):
    success: bool
    model_id: str
    code: str
    model_url: Optional[str] = None
    changes: Optional[str] = None
    error: Optional[str] = None


class ParameterUpdateRequest(BaseModel):
    model_id: str
    parameters: Dict[str, Any]


class AnalyzeRequest(BaseModel):
    model_id: str


class AnalyzeResponse(BaseModel):
    success: bool
    printable: bool
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    report: str


# ============================================================================
# Helpers
# ============================================================================

def _store_model(
    description: str,
    code: str,
    stl_bytes: Optional[bytes],
    step_bytes: Optional[bytes],
    metadata: Optional[dict],
    attempts: int = 1,
) -> ModelRecord:
    model_id = str(uuid.uuid4())
    glb_bytes = _stl_to_glb(stl_bytes) if stl_bytes else None
    record = ModelRecord(
        model_id=model_id,
        description=description,
        code=code,
        stl_bytes=stl_bytes,
        step_bytes=step_bytes,
        glb_bytes=glb_bytes,
        metadata=metadata,
        attempts=attempts,
    )
    _model_store[model_id] = record
    logger.info(f"Stored model {model_id} (GLB: {glb_bytes is not None})")
    return record


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    return {"name": "PromptForge API", "version": "0.1.0", "docs": "/docs"}


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    sandbox_manager = get_sandbox_manager()
    watsonx_client = get_watsonx_client()
    watsonx_health = watsonx_client.health_check()

    # Check ChromaDB health
    chroma_status = "unknown"
    try:
        from app.rag.chroma_client import ChromaClient
        chroma_client = ChromaClient()
        if chroma_client.health_check():
            chroma_status = "healthy"
        else:
            chroma_status = "unhealthy"
    except Exception as e:
        logger.warning(f"ChromaDB health check failed: {e}")
        chroma_status = "error"

    services = {
        "api": "healthy",
        "sandbox": "ready" if sandbox_manager.validate_image() else "not_ready",
        "watsonx": watsonx_health.get("status", "unknown"),
        "chroma": chroma_status,
    }
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.utcnow().isoformat(),
        services=services,
    )


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Main conversational endpoint. Routes user messages to the right agent.
    """
    from app.agents.router import classify_intent, answer_question
    from app.agents.generator import generate_model

    try:
        logger.info(f"Chat request: {request.message[:100]}")
        intent = classify_intent(request.message)

        if intent == "NEW_MODEL":
            result = generate_model(request.message)
            if not result.success:
                return ChatResponse(
                    message=f"I had trouble generating that model: {result.error}",
                    intent=intent,
                    error=result.error,
                )
            record = _store_model(
                description=request.message,
                code=result.code,
                stl_bytes=result.stl_bytes,
                step_bytes=result.step_bytes,
                metadata=result.metadata,
                attempts=result.attempts,
            )
            model_url = f"/api/model/{record.model_id}/glb"
            
            # Extract parameters for UI sliders
            parameters = None
            try:
                from app.agents.parameter_extractor import extract_parameters
                parameters = extract_parameters(result.code)
            except Exception as e:
                logger.warning(f"Parameter extraction failed: {e}")
            
            return ChatResponse(
                message=f"Here's your {request.message}! The 3D model is ready to view.",
                intent=intent,
                model_id=record.model_id,
                code=result.code,
                model_url=model_url,
                parameters=parameters,
            )

        elif intent == "QUESTION":
            answer = answer_question(request.message)
            return ChatResponse(message=answer, intent=intent)

        elif intent == "EXPORT":
            model_id = request.model_id
            if not model_id or model_id not in _model_store:
                return ChatResponse(
                    message="Please generate a model first before exporting.",
                    intent=intent,
                )
            return ChatResponse(
                message="Your model is ready to download.",
                intent=intent,
                model_id=model_id,
                model_url=f"/api/export/{model_id}/stl",
            )

        elif intent == "EDIT":
            model_id = request.model_id
            if not model_id or model_id not in _model_store:
                return ChatResponse(
                    message="Please generate a model first before editing it.",
                    intent=intent,
                )
            
            from app.agents.editor import edit_model as edit_model_agent
            record = _model_store[model_id]
            result = edit_model_agent(record.code, request.message)
            
            if not result.success:
                return ChatResponse(
                    message=f"I had trouble editing the model: {result.error}",
                    intent=intent,
                    error=result.error,
                )
            
            new_record = _store_model(
                description=f"{record.description} (edited: {request.message})",
                code=result.code,
                stl_bytes=result.stl_bytes,
                step_bytes=result.step_bytes,
                metadata=result.metadata,
                attempts=result.attempts,
            )
            
            return ChatResponse(
                message=f"I've updated your model! {result.changes or 'Changes applied successfully.'}",
                intent=intent,
                model_id=new_record.model_id,
                code=result.code,
                model_url=f"/api/model/{new_record.model_id}/glb",
            )
        
        else:
            return ChatResponse(
                message="I'm not sure how to help with that. Try asking me to create a model or answer a question.",
                intent=intent,
            )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/api/generate", response_model=GenerateResponse, tags=["Generation"])
async def generate_model_direct(request: GenerateRequest):
    """
    Direct model generation endpoint (bypasses chat routing).
    """
    from app.agents.generator import generate_model

    try:
        logger.info(f"Generate request: {request.description[:100]}")
        result = generate_model(request.description)

        if not result.success:
            return GenerateResponse(
                success=False,
                model_id="",
                code=result.code or "",
                error=result.error,
            )

        record = _store_model(
            description=request.description,
            code=result.code,
            stl_bytes=result.stl_bytes,
            step_bytes=result.step_bytes,
            metadata=result.metadata,
            attempts=result.attempts,
        )

        # Extract parameters for UI sliders
        parameters = None
        try:
            from app.agents.parameter_extractor import extract_parameters
            parameters = extract_parameters(result.code)
        except Exception as e:
            logger.warning(f"Parameter extraction failed: {e}")
        
        return GenerateResponse(
            success=True,
            model_id=record.model_id,
            code=result.code,
            model_url=f"/api/model/{record.model_id}/glb",
            metadata=result.metadata,
            parameters=parameters,
        )

    except SandboxExecutionError as e:
        logger.error(f"Sandbox error: {e}")
        raise HTTPException(status_code=500, detail=f"Code execution failed: {e}")
    except Exception as e:
        logger.error(f"Generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/model/{model_id}", tags=["Models"])
async def get_model(model_id: str):
    record = _model_store.get(model_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
    return {
        "model_id": record.model_id,
        "description": record.description,
        "code": record.code,
        "metadata": record.metadata,
        "created_at": record.created_at,
        "has_stl": record.stl_bytes is not None,
        "has_glb": record.glb_bytes is not None,
        "has_step": record.step_bytes is not None,
    }


@app.get("/api/model/{model_id}/glb", tags=["Models"])
async def get_model_glb(model_id: str):
    """Serve the GLB file for 3D viewing."""
    record = _model_store.get(model_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
    if not record.glb_bytes:
        raise HTTPException(status_code=404, detail="GLB not available for this model")
    return Response(
        content=record.glb_bytes,
        media_type="model/gltf-binary",
        headers={"Content-Disposition": f'attachment; filename="{model_id}.glb"'},
    )


@app.get("/api/export/{model_id}/{fmt}", tags=["Export"])
async def export_model(model_id: str, fmt: str):
    """Export model as STL, GLB, or STEP."""
    if fmt not in ("stl", "glb", "step"):
        raise HTTPException(status_code=400, detail=f"Unsupported format: {fmt}")

    record = _model_store.get(model_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")

    if fmt == "stl":
        data = record.stl_bytes
        media_type = "application/octet-stream"
    elif fmt == "glb":
        data = record.glb_bytes
        media_type = "model/gltf-binary"
    else:
        data = record.step_bytes
        media_type = "application/octet-stream"

    if not data:
        raise HTTPException(status_code=404, detail=f"{fmt.upper()} not available for this model")

    return Response(
        content=data,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{model_id}.{fmt}"'},
    )


@app.post("/api/edit", response_model=EditResponse, tags=["Editing"])
async def edit_model(request: EditRequest):
    """
    Edit an existing model based on natural language instruction.
    """
    from app.agents.editor import edit_model as edit_model_agent
    
    record = _model_store.get(request.model_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Model not found: {request.model_id}")
    
    try:
        logger.info(f"Editing model {request.model_id}: {request.instruction[:80]}")
        result = edit_model_agent(record.code, request.instruction)
        
        if not result.success:
            return EditResponse(
                success=False,
                model_id=request.model_id,
                code=result.code,
                error=result.error,
            )
        
        # Store the edited model as a new version
        new_record = _store_model(
            description=f"{record.description} (edited: {request.instruction})",
            code=result.code,
            stl_bytes=result.stl_bytes,
            step_bytes=result.step_bytes,
            metadata=result.metadata,
            attempts=result.attempts,
        )
        
        return EditResponse(
            success=True,
            model_id=new_record.model_id,
            code=result.code,
            model_url=f"/api/model/{new_record.model_id}/glb",
            changes=result.changes,
        )
    
    except Exception as e:
        logger.error(f"Edit error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/parameters", tags=["Parameters"])
async def update_parameters(request: ParameterUpdateRequest):
    """
    Update model parameters and regenerate the model.
    """
    record = _model_store.get(request.model_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Model not found: {request.model_id}")
    
    try:
        from app.agents.parameter_extractor import update_code_with_parameters
        
        # Update the code with new parameter values
        updated_code = update_code_with_parameters(record.code, request.parameters)
        
        # Execute the updated code
        sandbox = get_sandbox_manager()
        result = sandbox.execute(updated_code)
        
        if not result.get("success"):
            return {
                "success": False,
                "error": f"Failed to execute updated code: {result.get('error')}",
            }
        
        # Store the updated model
        files = result.get("files", {})
        new_record = _store_model(
            description=f"{record.description} (parameters updated)",
            code=updated_code,
            stl_bytes=files.get("output.stl"),
            step_bytes=files.get("output.step"),
            metadata=result.get("metadata"),
            attempts=1,
        )
        
        return {
            "success": True,
            "model_id": new_record.model_id,
            "model_url": f"/api/model/{new_record.model_id}/glb",
        }
    
    except Exception as e:
        logger.error(f"Parameter update error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_printability(request: AnalyzeRequest):
    """
    Perform comprehensive print-readiness analysis on a 3D model.
    Uses geometric analysis and AI-powered report generation.
    """
    record = _model_store.get(request.model_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Model not found: {request.model_id}")

    if not record.stl_bytes:
        return AnalyzeResponse(
            success=False,
            printable=False,
            issues=[],
            recommendations=[],
            report="No STL available to analyze",
        )

    try:
        # Save STL to temporary file for analysis
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp_file:
            tmp_file.write(record.stl_bytes)
            tmp_path = Path(tmp_file.name)
        
        try:
            # Run geometric analysis
            analyzer = GeometricAnalyzer(print_technology="fdm")
            analysis_result: AnalysisResult = analyzer.analyze_model(tmp_path)
            
            # Convert AnalysisResult to dict for prompt
            analysis_dict = {
                "status": analysis_result.status,
                "issues": [
                    {
                        "severity": issue.severity,
                        "category": issue.category,
                        "message": issue.message,
                        "details": issue.details,
                        "suggestion": issue.suggestion
                    }
                    for issue in analysis_result.issues
                ],
                "metadata": analysis_result.metadata,
                "recommendations": analysis_result.recommendations
            }
            
            # Generate AI-powered report
            try:
                watsonx = get_watsonx_client()
                system_prompt, user_prompt = build_analysis_report_prompt(analysis_dict)
                
                params = GenerationParams(
                    max_tokens=800,
                    temperature=0.3,
                    top_p=0.9
                )
                
                ai_report = watsonx.generate(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    params=params
                )
                report = ai_report.strip()
            except Exception as e:
                logger.warning(f"AI report generation failed, using basic report: {e}")
                # Fallback to basic report
                status_emoji = {"ready": "✅", "needs_attention": "⚠️", "not_printable": "❌"}.get(
                    analysis_result.status, "ℹ️"
                )
                report = f"{status_emoji} Analysis Status: {analysis_result.status}\n\n"
                if analysis_result.issues:
                    report += "Issues found:\n"
                    for issue in analysis_result.issues:
                        report += f"- [{issue.severity.upper()}] {issue.message}\n"
                else:
                    report += "No issues detected - model looks good!\n"
                
                if analysis_result.recommendations:
                    report += "\nRecommendations:\n"
                    for rec in analysis_result.recommendations:
                        report += f"- {rec}\n"
            
            # Convert issues to API format
            issues_api = [
                {
                    "type": issue.category,
                    "description": issue.message,
                    "severity": issue.severity
                }
                for issue in analysis_result.issues
            ]
            
            # Determine printability
            printable = analysis_result.status in ["ready", "needs_attention"]
            
            return AnalyzeResponse(
                success=True,
                printable=printable,
                issues=issues_api,
                recommendations=analysis_result.recommendations,
                report=report,
            )
        
        finally:
            # Clean up temporary file
            try:
                tmp_path.unlink()
            except Exception:
                pass
    
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        return AnalyzeResponse(
            success=False,
            printable=False,
            issues=[],
            recommendations=[],
            report=f"Analysis failed: {str(e)}",
        )


# ============================================================================
# Startup / Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    logger.info("Starting PromptForge API...")
    
    # Initialize sandbox
    sandbox_manager = get_sandbox_manager()
    if not sandbox_manager.validate_image():
        logger.warning("Sandbox image not found. Run: docker build -t promptforge-sandbox backend/sandbox/")
    else:
        logger.info(f"Sandbox image ready: {sandbox_manager.image}")

    # Initialize watsonx.ai
    try:
        watsonx_client = get_watsonx_client()
        health = watsonx_client.health_check()
        if health.get("status") == "healthy":
            logger.info(f"watsonx.ai ready: {health.get('model_id')}")
        else:
            logger.warning(f"watsonx.ai unhealthy: {health.get('error')}")
    except Exception as e:
        logger.error(f"Failed to initialize watsonx.ai client: {e}")
    
    # Initialize ChromaDB
    try:
        from app.rag.chroma_client import ChromaClient
        chroma_client = ChromaClient()
        chroma_client.initialize()
        
        # Get collection counts
        counts = {
            "cadquery_docs": chroma_client.get_collection_count("cadquery_docs"),
            "design_patterns": chroma_client.get_collection_count("design_patterns"),
            "few_shot_examples": chroma_client.get_collection_count("few_shot_examples"),
        }
        logger.info(f"ChromaDB ready: {counts}")
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB: {e}")

    logger.info("PromptForge API started")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down PromptForge API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
