#!/usr/bin/env python3
"""
Compliance QA API - FastAPI Application
Uses TidyLLM as library for AI/ML functionality
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import sys
from pathlib import Path
from datetime import datetime

# Import TidyLLM as library (assuming it's installed/importable)
try:
    from packages.tidyllm.services.unified_chat_manager import UnifiedChatManager, ChatMode
    from packages.tidyllm.gateways.corporate_llm_gateway import CorporateLLMGateway
except ImportError as e:
    # Fallback if package structure changes
    try:
        from tidyllm.services.unified_chat_manager import UnifiedChatManager, ChatMode
        from tidyllm.gateways.corporate_llm_gateway import CorporateLLMGateway
    except ImportError as e2:
        print(f"Warning: TidyLLM import failed: {e} / {e2}")
        UnifiedChatManager = None
        ChatMode = None
        CorporateLLMGateway = None

# API Models
class ChatRequest(BaseModel):
    message: str
    mode: Optional[str] = "direct"
    model: Optional[str] = "claude-3-sonnet"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

class ChatResponse(BaseModel):
    response: str
    mode: str
    model: str
    timestamp: str

class QARequest(BaseModel):
    document_path: str
    question: str
    mode: Optional[str] = "rag"

class HealthResponse(BaseModel):
    status: str
    version: str
    components: Dict[str, bool]

# Initialize FastAPI
app = FastAPI(
    title="Compliance QA API",
    description="Enterprise AI Platform powered by TidyLLM",
    version="0.1.0"
)

# Initialize services
chat_manager = None
if UnifiedChatManager:
    try:
        chat_manager = UnifiedChatManager()
    except Exception as e:
        print(f"Warning: Could not initialize chat manager: {e}")

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Compliance QA API",
        "version": "0.1.0",
        "description": "Enterprise AI Platform powered by TidyLLM",
        "endpoints": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    components = {
        "tidyllm": UnifiedChatManager is not None,
        "chat_manager": chat_manager is not None,
        "corporate_gateway": CorporateLLMGateway is not None
    }

    return HealthResponse(
        status="healthy" if all(components.values()) else "degraded",
        version="0.1.0",
        components=components
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat with AI models using TidyLLM."""
    if not chat_manager:
        raise HTTPException(
            status_code=503,
            detail="Chat service not available - TidyLLM not properly initialized"
        )

    try:
        # Use TidyLLM chat manager
        mode = ChatMode(request.mode) if ChatMode else request.mode
        response = chat_manager.chat(
            message=request.message,
            mode=mode,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        return ChatResponse(
            response=response,
            mode=request.mode,
            model=request.model,
            timestamp=str(datetime.utcnow())
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/qa")
async def qa_endpoint(request: QARequest):
    """QA processing endpoint."""
    # This would integrate with parent-level QA processing
    return {
        "message": "QA processing endpoint - integration with compliance QA processor",
        "document": request.document_path,
        "question": request.question,
        "mode": request.mode
    }

@app.get("/models")
async def list_models():
    """List available AI models."""
    try:
        # Get available models from TidyLLM configuration
        return {
            "models": [
                "claude-3-haiku",
                "claude-3-sonnet",
                "claude-3-5-sonnet",
                "claude-3-opus"
            ],
            "default": "claude-3-sonnet"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not list models: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)