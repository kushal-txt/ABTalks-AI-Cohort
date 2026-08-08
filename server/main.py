import os
import json
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from server.models import InterviewRequest, InterviewResponse
from server.agent import handle_start_interview, handle_conversation_turn, get_llm_provider

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANDIDATES_PATH = os.path.join(BASE_DIR, "data", "candidates.json")
CURRICULUM_PATH = os.path.join(BASE_DIR, "data", "curriculum.json")
STATIC_PATH = os.path.join(BASE_DIR, "static")

app = FastAPI(title="ABTalks AI Interviewer Server")

# Request logging middleware for Vercel path debugging
from fastapi import Request
@app.middleware("http")
async def log_request(request: Request, call_next):
    print(f"[Request Log] Method: {request.method} Path: {request.url.path}")
    response = await call_next(request)
    print(f"[Response Log] Status: {response.status_code}")
    return response

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
        with open(CANDIDATES_PATH, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load candidates: {str(e)}")

# Helper endpoint to get curriculum
@app.get("/api/curriculum")
async def get_curriculum():
    try:
        with open(CURRICULUM_PATH, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load curriculum: {str(e)}")

# Settings request model
class SettingsRequest(BaseModel):
    gemini_key: Optional[str] = None
    openai_key: Optional[str] = None
    openrouter_key: Optional[str] = None

# Settings endpoint to configure/save API keys dynamically
@app.post("/api/settings")
async def update_settings(req: SettingsRequest):
    try:
        # Load existing env vars to preserve keys not in current request
        env_vars = {}
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            env_vars[parts[0].strip()] = parts[1].strip()
        
        # Apply updates or removals
        if req.gemini_key is not None:
            val = req.gemini_key.strip()
            if val == "":
                env_vars.pop("GEMINI_API_KEY", None)
                os.environ.pop("GEMINI_API_KEY", None)
            else:
                env_vars["GEMINI_API_KEY"] = val
                os.environ["GEMINI_API_KEY"] = val
                
        if req.openai_key is not None:
            val = req.openai_key.strip()
            if val == "":
                env_vars.pop("OPENAI_API_KEY", None)
                os.environ.pop("OPENAI_API_KEY", None)
            else:
                env_vars["OPENAI_API_KEY"] = val
                os.environ["OPENAI_API_KEY"] = val
                
        if req.openrouter_key is not None:
            val = req.openrouter_key.strip()
            if val == "":
                env_vars.pop("OPENROUTER_API_KEY", None)
                os.environ.pop("OPENROUTER_API_KEY", None)
            else:
                env_vars["OPENROUTER_API_KEY"] = val
                os.environ["OPENROUTER_API_KEY"] = val
            
        # Write back all variables to .env
        env_lines = []
        for k, v in env_vars.items():
            env_lines.append(f"{k}={v}")
            
        with open(".env", "w") as f:
            f.write("\n".join(env_lines) + "\n")
            
        # Re-import or re-load in agent if necessary (os.environ is shared anyway)
        return {
            "status": "success", 
            "active_provider": get_llm_provider()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save settings: {str(e)}")

@app.get("/api/settings")
async def get_settings():
    return {
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "openrouter_configured": bool(os.getenv("OPENROUTER_API_KEY")),
        "active_provider": get_llm_provider()
    }

# Mount static files at root (FastAPI will check endpoints first, then static files)
app.mount("/", StaticFiles(directory=STATIC_PATH, html=True), name="static")
