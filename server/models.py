from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class CandidateMember(BaseModel):
    id: str
    name: str
    jobRole: str
    yearsExperience: int
    education: str
    status: str

class CandidateMission(BaseModel):
    day: int
    title: str
    passed: Optional[bool] = None
    attempts: Optional[int] = None
    skipped: Optional[bool] = None

class CandidateSignals(BaseModel):
    commitDays: int
    missionsCompleted: int
    missionsFirstTry: int

class CandidateProfile(BaseModel):
    member: CandidateMember
    missions: List[CandidateMission]
    signals: CandidateSignals

class InterviewRequest(BaseModel):
    sessionId: str
    candidate: Optional[CandidateProfile] = None
    message: Optional[str] = None

class FeedbackReport(BaseModel):
    summary: str
    strengths: List[str]
    gaps: List[str]
    next: List[str]
    decision: str

class InterviewResponse(BaseModel):
    reply: str
    done: bool
    feedback: Optional[FeedbackReport] = None
