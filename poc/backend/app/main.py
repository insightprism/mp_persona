#!/usr/bin/env python3
"""
Persona Chat System - FastAPI Backend
====================================

Main FastAPI application for the persona chat MVP web interface.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from persona_config import PersonaConfig
from llm_persona_firefly import LLMPersonaFirefly
from persona_llm_adapter import PersonaLLMAdapter
from persona_image_generator import generate_persona_image_simple
from persona_voice_generator import generate_persona_voice_simple
from cost_optimizer import PersonaCostOptimizer

# FastAPI app setup
app = FastAPI(
    title="Persona Chat System API",
    description="Backend API for multi-model persona chat interface",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8001", "http://127.0.0.1:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for MVP (replace with database in production)
class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.personas: Dict[str, Dict] = {}
        self.connections: Dict[str, WebSocket] = {}
        self.llm_adapter = PersonaLLMAdapter()
        self.cost_optimizer = PersonaCostOptimizer()
    
    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "personas": [],
            "messages": {}
        }
        return session_id
    
    def create_persona(self, session_id: str, persona_data: dict) -> str:
        persona_id = str(uuid.uuid4())
        
        # Create PersonaConfig from input data
        persona_config = PersonaConfig(
            name=persona_data["name"],
            age=persona_data["age"],
            race_ethnicity=persona_data["race_ethnicity"],
            gender=persona_data["gender"],
            education=persona_data["education"],
            location_type=persona_data["location_type"],
            income=persona_data["income"]
        )
        
        # Create firefly instance
        firefly = LLMPersonaFirefly(persona_config, purpose=f"web_chat_{persona_id}")
        
        # Set LLM configuration if provided
        if persona_data.get("llm_provider") and persona_data.get("llm_api_key"):
            firefly.set_llm_config(
                persona_data["llm_provider"],
                persona_data["llm_api_key"],
                persona_data.get("llm_model")
            )
        
        # Store persona
        self.personas[persona_id] = {
            "id": persona_id,
            "session_id": session_id,
            "config": persona_data,
            "persona_config": persona_config,
            "firefly": firefly,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        # Add to session
        if session_id in self.sessions:
            self.sessions[session_id]["personas"].append(persona_id)
            self.sessions[session_id]["messages"][persona_id] = []
        
        return persona_id
    
    async def chat_with_persona(self, persona_id: str, message: str) -> dict:
        if persona_id not in self.personas:
            raise ValueError("Persona not found")
        
        persona = self.personas[persona_id]
        firefly = persona["firefly"]
        
        try:
            response = await firefly.glow({
                "prompt": message,
                "disappear": False  # Keep alive for continued chat
            })
            
            # Track interaction for cost optimization
            usage = response.get("usage", {})
            if usage:
                usage["provider"] = response.get("provider", "unknown")
                self.cost_optimizer.track_interaction(persona_id, usage)
            else:
                self.cost_optimizer.track_interaction(persona_id)
            
            return {
                "persona_id": persona_id,
                "user_message": message,
                "persona_response": response.get("persona_response", ""),
                "timestamp": datetime.utcnow().isoformat(),
                "provider": response.get("provider", "unknown"),
                "usage": response.get("usage", {}),
                "success": True
            }
        except Exception as e:
            return {
                "persona_id": persona_id,
                "user_message": message,
                "persona_response": f"Error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
                "success": False,
                "error": str(e)
            }

# Global session manager
session_manager = SessionManager()

# Data models (Pydantic)
from pydantic import BaseModel

class PersonaCreate(BaseModel):
    name: str
    age: int
    race_ethnicity: str
    gender: str
    education: str
    location_type: str
    income: str
    llm_provider: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_model: Optional[str] = None

class ChatMessage(BaseModel):
    message: str
    persona_id: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    created_at: str

class PersonaResponse(BaseModel):
    persona_id: str
    session_id: str
    name: str
    status: str
    llm_provider: str
    llm_model: str
    created_at: str

# API Routes

@app.get("/")
async def root():
    return {"message": "Persona Chat System API", "version": "1.0.0"}

@app.post("/api/sessions/", response_model=SessionResponse)
async def create_session():
    """Create a new chat session"""
    session_id = session_manager.create_session()
    session = session_manager.sessions[session_id]
    return SessionResponse(
        session_id=session_id,
        created_at=session["created_at"]
    )

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details and personas"""
    if session_id not in session_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = session_manager.sessions[session_id]
    personas = []
    
    for persona_id in session["personas"]:
        if persona_id in session_manager.personas:
            persona = session_manager.personas[persona_id]
            firefly = persona["firefly"]
            personas.append({
                "id": persona_id,
                "name": persona["config"]["name"],
                "status": persona["status"],
                "llm_provider": firefly.llm_provider,
                "llm_model": firefly.llm_model,
                "created_at": persona["created_at"]
            })
    
    return {
        "session_id": session_id,
        "created_at": session["created_at"],
        "personas": personas
    }

@app.post("/api/sessions/{session_id}/personas/")
async def create_persona(session_id: str, persona_data: PersonaCreate):
    """Create a new persona in a session"""
    if session_id not in session_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        persona_id = session_manager.create_persona(session_id, persona_data.dict())
        persona = session_manager.personas[persona_id]
        firefly = persona["firefly"]
        
        return {
            "persona_id": persona_id,
            "session_id": session_id,
            "name": persona_data.name,
            "status": "active",
            "llm_provider": firefly.llm_provider,
            "llm_model": firefly.llm_model,
            "created_at": persona["created_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/personas/{persona_id}/chat")
async def chat_with_persona(persona_id: str, message: ChatMessage):
    """Send a message to a specific persona"""
    try:
        response = await session_manager.chat_with_persona(persona_id, message.message)
        
        # Store message in session
        for session in session_manager.sessions.values():
            if persona_id in session.get("messages", {}):
                session["messages"][persona_id].append(response)
                break
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/personas/{persona_id}/messages")
async def get_persona_messages(persona_id: str):
    """Get chat history for a persona"""
    # Find session containing this persona
    for session in session_manager.sessions.values():
        if persona_id in session.get("messages", {}):
            return {
                "persona_id": persona_id,
                "messages": session["messages"][persona_id]
            }
    
    raise HTTPException(status_code=404, detail="Persona not found")

@app.get("/api/models/available")
async def get_available_models():
    """Get available LLM models and providers"""
    llm_adapter = PersonaLLMAdapter()
    
    # Check what's actually available
    models = {
        "openai": {
            "available": bool(os.getenv("OPENAI_API_KEY")),
            "models": ["gpt-4", "gpt-3.5-turbo"],
            "requires_key": True
        },
        "claude": {
            "available": bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")),
            "models": ["claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
            "requires_key": True
        },
        "ollama_local": {
            "available": _check_ollama_available(),
            "models": _get_ollama_models(),
            "requires_key": False
        }
    }
    
    return {
        "providers": models,
        "default_models": llm_adapter.get_default_models()
    }

def _check_ollama_available() -> bool:
    """Check if Ollama is running locally"""
    try:
        import httpx
        with httpx.Client(timeout=2.0) as client:
            response = client.get("http://localhost:11434/api/tags")
            return response.status_code == 200
    except:
        return False

def _get_ollama_models() -> List[str]:
    """Get available Ollama models"""
    try:
        import httpx
        with httpx.Client(timeout=2.0) as client:
            response = client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
    except:
        pass
    return ["llama3:8b", "mistral:7b"]  # Fallback defaults

# WebSocket for real-time chat
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    session_manager.connections[session_id] = websocket
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            persona_id = message_data.get("persona_id")
            message = message_data.get("message")
            
            if not persona_id or not message:
                await websocket.send_text(json.dumps({
                    "error": "Missing persona_id or message"
                }))
                continue
            
            # Process chat message
            try:
                response = await session_manager.chat_with_persona(persona_id, message)
                
                # Send response back to client
                await websocket.send_text(json.dumps(response))
                
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "error": str(e),
                    "persona_id": persona_id
                }))
    
    except WebSocketDisconnect:
        if session_id in session_manager.connections:
            del session_manager.connections[session_id]

# Cost recommendation endpoints
@app.get("/api/personas/{persona_id}/cost-recommendations")
async def get_cost_recommendations(persona_id: str):
    """Get cost recommendations for asset generation"""
    if persona_id not in session_manager.personas:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    optimizer = session_manager.cost_optimizer
    
    image_rec = optimizer.should_generate_image(persona_id)
    voice_rec = optimizer.should_generate_voice(persona_id)
    usage_stats = optimizer.get_persona_usage(persona_id)
    
    return {
        "persona_id": persona_id,
        "recommendations": {
            "image": image_rec,
            "voice": voice_rec
        },
        "usage_stats": usage_stats,
        "cost_summary": {
            "total_cost": usage_stats["total_cost"],
            "cost_per_interaction": usage_stats["cost_per_interaction"],
            "projected_image_cost": 0.02,
            "projected_voice_cost": 0.003
        }
    }

# Asset generation endpoints  
@app.post("/api/personas/{persona_id}/generate-image")
async def generate_persona_image(persona_id: str, force: bool = False):
    """Generate profile image for persona"""
    if persona_id not in session_manager.personas:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    # Check cost recommendation unless forced
    if not force:
        optimizer = session_manager.cost_optimizer
        recommendation = optimizer.should_generate_image(persona_id)
        
        if not recommendation["recommend"]:
            return {
                "success": False,
                "recommendation": recommendation,
                "message": "Image generation not recommended based on usage pattern",
                "alternatives": recommendation.get("alternatives", []),
                "force_url": f"/api/personas/{persona_id}/generate-image?force=true"
            }
    
    persona = session_manager.personas[persona_id]
    persona_config = persona["persona_config"]
    
    try:
        result = generate_persona_image_simple(persona_config)
        
        # Track cost
        if result["success"]:
            session_manager.cost_optimizer.track_asset_generation(
                persona_id, "image", 0.02
            )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/personas/{persona_id}/generate-voice")
async def generate_persona_voice(persona_id: str, custom_text: str = None):
    """Generate voice sample for persona"""
    if persona_id not in session_manager.personas:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    # Check cost recommendation
    optimizer = session_manager.cost_optimizer
    recommendation = optimizer.should_generate_voice(persona_id, custom_text)
    
    persona = session_manager.personas[persona_id]
    persona_config = persona["persona_config"]
    
    try:
        if custom_text:
            result = generate_persona_voice_simple(persona_config, custom_text=custom_text)
        else:
            result = generate_persona_voice_simple(persona_config)
        
        # Track cost
        if result["success"]:
            cost = recommendation["cost"]
            session_manager.cost_optimizer.track_asset_generation(
                persona_id, "voice", cost
            )
        
        # Add recommendation info to response
        result["cost_recommendation"] = recommendation
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cost-summary")
async def get_cost_summary():
    """Get overall cost summary"""
    return session_manager.cost_optimizer.get_cost_summary()

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "ollama": _check_ollama_available(),
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "claude": bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY"))
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)