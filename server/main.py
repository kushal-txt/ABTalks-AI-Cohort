import os
import json
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from server.models import InterviewRequest, InterviewResponse
from server.agent import handle_start_interview, handle_conversation_turn

app = FastAPI(title="ABTalks AI Interviewer Server")

# Allow CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoint defined in Technical Specification
@app.post("/api/interview", response_model=InterviewResponse)
async def interview_endpoint(req: InterviewRequest):
    session_id = req.sessionId
    
    # 1. Start Interview (request contains candidate but no message)
    if req.candidate is not None:
        try:
            return handle_start_interview(session_id, req.candidate)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")
            
    # 2. Conversation Turn (request contains message)
    elif req.message is not None:
        try:
            return handle_conversation_turn(session_id, req.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process turn: {str(e)}")
            
    else:
        raise HTTPException(
            status_code=400, 
            detail="Invalid request. Must provide 'candidate' (to start) or 'message' (to continue)."
        )

# Helper endpoint to get all candidates
@app.get("/api/candidates")
async def get_candidates():
    try:
        with open("data/candidates.json", "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load candidates: {str(e)}")

# Helper endpoint to get curriculum
@app.get("/api/curriculum")
async def get_curriculum():
    try:
        with open("data/curriculum.json", "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load curriculum: {str(e)}")

# Settings request model
class SettingsRequest(BaseModel):
    gemini_key: Optional[str] = None
    openai_key: Optional[str] = None

# Settings endpoint to configure/save API keys dynamically
@app.post("/api/settings")
async def update_settings(req: SettingsRequest):
    try:
        env_lines = []
        if req.gemini_key is not None:
            # Mask or unmask? We store the actual value.
            env_lines.append(f"GEMINI_API_KEY={req.gemini_key.strip()}")
            os.environ["GEMINI_API_KEY"] = req.gemini_key.strip()
        if req.openai_key is not None:
            env_lines.append(f"OPENAI_API_KEY={req.openai_key.strip()}")
            os.environ["OPENAI_API_KEY"] = req.openai_key.strip()
            
        with open(".env", "w") as f:
            f.write("\n".join(env_lines) + "\n")
            
        # Re-import or re-load in agent if necessary (os.environ is shared anyway)
        return {
            "status": "success", 
            "active_provider": "gemini" if req.gemini_key else ("openai" if req.openai_key else "mock")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save settings: {str(e)}")

@app.get("/api/settings")
async def get_settings():
    return {
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "active_provider": "gemini" if os.getenv("GEMINI_API_KEY") else ("openai" if os.getenv("OPENAI_API_KEY") else "mock")
    }

# Mount static files at root (FastAPI will check endpoints first, then static files)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
