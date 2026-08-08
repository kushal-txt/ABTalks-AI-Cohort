import os
import json
import random
import time
import requests
import re
from typing import Dict, Any, List, Optional
from server.models import CandidateProfile, FeedbackReport, InterviewResponse
from server.questions_db import QUESTIONS_DB
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURRICULUM_PATH = os.path.join(BASE_DIR, "data", "curriculum.json")

# Check for API Keys
def get_llm_provider() -> str:
    """Determine which LLM provider to use based on env variables."""
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    openrouter_fallback = os.getenv("OPENROUTER_API_KEY_FALLBACK")
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    use_ollama = os.getenv("USE_OLLAMA", "").lower() == "true"
    
    if openrouter_key or openrouter_fallback:
        return "openrouter"
    elif gemini_key:
        return "gemini"
    elif openai_key:
        return "openai"
    elif use_ollama:
        return "ollama"
    return "none"

def extract_json(text: str) -> Dict[str, Any]:
    """Helper to extract and parse the JSON object from raw LLM responses.
    Filters out conversational prefix/suffix or markdown code block markers.
    """
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
        raise ValueError("Could not find a valid JSON block inside the LLM output.")
    
    json_str = text[start_idx:end_idx + 1]
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        import re
        # Remove trailing commas before closing braces/brackets
        cleaned_str = re.sub(r',\s*([\]}])', r'\1', json_str)
        try:
            return json.loads(cleaned_str)
        except Exception:
            raise e

def ensure_list_of_strings(val: Any) -> List[str]:
    """Coerces any input format into a list of strings.
    Prevents Pydantic validation errors if the LLM returned a string instead of a list of strings.
    """
    if isinstance(val, list):
        return [str(item).strip() for item in val if str(item).strip()]
    elif isinstance(val, str):
        cleaned = val.strip()
        if cleaned:
            # If it's a bulleted string, split it
            if "\n" in cleaned:
                lines = [re.sub(r'^[-*•\d.]+\s*', '', line).strip() for line in cleaned.split("\n")]
                return [line for line in lines if line]
            return [cleaned]
        return []
    elif val is None:
        return []
    else:
        return [str(val).strip()]

def call_openrouter_with_history(system_prompt: str, history: List[Dict[str, str]], guidance: str, max_tokens: int = 256) -> str:
    """Helper to call OpenRouter API with full conversation history and explicit token limits.
    Utilizes a key rotation list to fall back if a key runs out of credits or encounters an error.
    """
    keys = []
    
    # Load primary key
    primary_key = os.getenv("OPENROUTER_API_KEY")
    if primary_key:
        keys.append(primary_key)
        
    # Load fallback key
    fallback_key = os.getenv("OPENROUTER_API_KEY_FALLBACK")
    if fallback_key:
        keys.append(fallback_key)
        
    model_name = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
    
    last_error = None
    for idx, key in enumerate(keys):
        if not key:
            continue
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=key,
            )
            
            messages = [{"role": "system", "content": system_prompt}]
            for turn in history:
                role = "assistant" if turn["role"] == "interviewer" else "user"
                messages.append({"role": role, "content": turn["content"]})
            
            messages.append({"role": "system", "content": f"[GUIDANCE FOR THIS TURN]:\n{guidance}"})
            
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "ABTalks AI Interviewer Agent"
                },
                temperature=0.7,
                timeout=18.0
            )
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            print(f"[Warning] OpenRouter key {idx+1} failed. Error: {str(e)}")
            continue
            
    return f"Error calling OpenRouter: All keys failed. Last error: {str(last_error)}"

def call_gemini_with_history(system_prompt: str, history: List[Dict[str, str]], guidance: str) -> str:
    """Helper to call Gemini API with full conversation history."""
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=gemini_key)
        
        contents = []
        for turn in history:
            role = "model" if turn["role"] == "interviewer" else "user"
            contents.append(types.Content(
                role=role,
                parts=[types.Part.from_text(text=turn["content"])]
            ))
            
        full_system_instruction = f"{system_prompt}\n\n[GUIDANCE FOR THIS TURN]:\n{guidance}"
        
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=full_system_instruction,
                temperature=0.7,
            )
        )
        return response.text
    except Exception as e1:
        try:
            import google.generativeai as google_genai
            google_genai.configure(api_key=gemini_key)
            classic_model_name = "gemini-1.5-flash" if model_name == "gemini-2.5-flash" else model_name
            full_system_instruction = f"{system_prompt}\n\n[GUIDANCE FOR THIS TURN]:\n{guidance}"
            model = google_genai.GenerativeModel(
                model_name=classic_model_name,
                system_instruction=full_system_instruction
            )
            
            classic_contents = []
            for turn in history:
                role = "model" if turn["role"] == "interviewer" else "user"
                classic_contents.append({
                    "role": role,
                    "parts": [turn["content"]]
                })
                
            response = model.generate_content(classic_contents)
            return response.text
        except Exception as e2:
            return f"Error calling Gemini: {str(e1)} | {str(e2)}"

def call_openai_with_history(system_prompt: str, history: List[Dict[str, str]], guidance: str, max_tokens: int = 256) -> str:
    """Helper to call OpenAI API with full conversation history."""
    openai_key = os.getenv("OPENAI_API_KEY", "")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        for turn in history:
            role = "assistant" if turn["role"] == "interviewer" else "user"
            messages.append({"role": role, "content": turn["content"]})
            
        messages.append({"role": "system", "content": f"[GUIDANCE FOR THIS TURN]:\n{guidance}"})
        
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling OpenAI: {str(e)}"

def call_ollama_with_history(system_prompt: str, history: List[Dict[str, str]], guidance: str) -> str:
    """Helper to call local Ollama instance with full conversation history."""
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
    model_name = os.getenv("OLLAMA_MODEL", "qwen2.5-coder")
    try:
        messages = [{"role": "system", "content": system_prompt}]
        for turn in history:
            role = "assistant" if turn["role"] == "interviewer" else "user"
            messages.append({"role": role, "content": turn["content"]})
            
        messages.append({"role": "system", "content": f"[GUIDANCE FOR THIS TURN]:\n{guidance}"})
        
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.7
            }
        }
        
        resp = requests.post(ollama_url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "")
    except Exception as e:
        return f"Error calling local Ollama: {str(e)}. Make sure Ollama is running and model '{model_name}' is downloaded."

def call_llm(system_prompt: str, history: List[Dict[str, str]], guidance: str, max_tokens: int = 256) -> str:
    """Routes the generation request to the selected LLM provider, wrapped with retry logic."""
    provider = get_llm_provider()
    
    retries = 3
    delay = 1.0
    last_error_msg = ""
    
    for attempt in range(retries):
        try:
            if provider == "openrouter":
                res = call_openrouter_with_history(system_prompt, history, guidance, max_tokens)
            elif provider == "gemini":
                res = call_gemini_with_history(system_prompt, history, guidance)
            elif provider == "openai":
                res = call_openai_with_history(system_prompt, history, guidance, max_tokens)
            elif provider == "ollama":
                res = call_ollama_with_history(system_prompt, history, guidance)
            else:
                return "Mock Mode: API Keys not set."
            
            if res.startswith("Error calling"):
                raise Exception(res)
            return res
        except Exception as e:
            last_error_msg = str(e)
            print(f"[Retry Warning] Attempt {attempt+1} failed: {last_error_msg}. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2
            
    return f"Error calling LLM after {retries} attempts. Last error: {last_error_msg}"


class InterviewSessionState:
    """Stores the active state of an interview session in memory."""
    def __init__(self, session_id: str, candidate: CandidateProfile):
        self.session_id = session_id
        self.candidate = candidate
        self.history: List[Dict[str, str]] = []  # list of {"role": "interviewer" or "candidate", "content": "..."}
        
        # Select 4 days completed by the candidate
        self.selected_days = self._select_curriculum_days()
        self.current_step = 0  # 0 to 9
        
    def _select_curriculum_days(self) -> List[int]:
        """Selects 4 distinct curriculum days that the candidate completed."""
        passed_days = [m.day for m in self.candidate.missions if m.passed]
        
        if len(passed_days) < 4:
            all_days = list(range(1, 32))
            for d in all_days:
                if d not in passed_days:
                    passed_days.append(d)
                if len(passed_days) >= 4:
                    break
        
        passed_days = sorted(list(set(passed_days)))
        
        if len(passed_days) <= 4:
            return passed_days
            
        # Select a spread of 4 days
        n = len(passed_days)
        selected = [
            passed_days[0],
            passed_days[n // 3],
            passed_days[(2 * n) // 3],
            passed_days[-1]
        ]
        
        return sorted(list(set(selected)))

    def get_day_for_step(self, step: int) -> int:
        """Helper to get which curriculum day a step corresponds to."""
        day_idx = (step - 1) // 2
        if 0 <= day_idx < len(self.selected_days):
            return self.selected_days[day_idx]
        return self.selected_days[-1]


# In-memory session store
sessions_db: Dict[str, InterviewSessionState] = {}


def load_curriculum_day_details(day_num: int) -> Dict[str, Any]:
    """Loads curriculum details for a specific day from curriculum.json."""
    try:
        with open(CURRICULUM_PATH, "r") as f:
            data = json.load(f)
        for d in data.get("days", []):
            if d.get("day") == day_num:
                return d
    except Exception:
        pass
    return {
        "day": day_num,
        "title": f"Cohort Day {day_num}",
        "tools": [],
        "objectives": ["Understand the daily learning objectives."]
    }


def handle_start_interview(session_id: str, candidate: CandidateProfile) -> InterviewResponse:
    """Initializes a new interview session and returns a welcoming message."""
    session = InterviewSessionState(session_id, candidate)
    sessions_db[session_id] = session
    
    provider = get_llm_provider()
    if provider == "none":
        err_msg = (
            "API key not found. Please click the Settings icon in the top right to configure your API keys "
            "(OpenRouter, Gemini, or OpenAI) before starting the interview. Mock Simulator Mode has been disabled."
        )
        return InterviewResponse(reply=err_msg, done=False)
        
    candidate_name = candidate.member.name
    job_role = candidate.member.jobRole
    exp = candidate.member.yearsExperience
    
    # Get details for the 4 days we selected
    day_titles = []
    for d in session.selected_days:
        details = load_curriculum_day_details(d)
        day_titles.append(f"Day {d} ({details.get('title')})")
        
    system_prompt = (
        f"You are Alex, a demanding, direct, and highly rigorous Senior AI Architect conducting a technical interview "
        f"for {candidate_name}, who is applying after finishing the ABTalks AI Cohort.\n"
        f"The candidate has a background as a {job_role} with {exp} years of experience.\n"
        f"Always refer to yourself as Alex, the Lead AI Architect. Speak clearly and professionally. "
        f"Never use placeholders like '[Your Name]' or '[Interviewer Name]'. Introduce yourself simply as Alex."
    )
    
    welcome_guidance = (
        f"Introduce yourself as Alex, the Lead AI Architect. Welcome the candidate. "
        f"State clearly that you will be interviewing them on 4 key topics from their cohort:\n"
        f"- " + "\n- ".join(day_titles) + "\n\n"
        f"Ask them if they are ready to begin. Keep it welcoming but professional and under 4 sentences. "
        f"Do not write '[Your Name]' or '[Interviewer Name]' under any circumstances."
    )
    
    reply = call_llm(system_prompt, [], welcome_guidance)
        
    # Save the welcome message to history
    session.history.append({"role": "interviewer", "content": reply})
    session.current_step = 1  
    
    return InterviewResponse(reply=reply, done=False)


def handle_conversation_turn(session_id: str, candidate_message: str) -> InterviewResponse:
    """Processes a user message, progresses the state machine, and returns the next question or final feedback."""
    if session_id not in sessions_db:
        return InterviewResponse(reply="Session not found. Please start the interview first.", done=False)
        
    session = sessions_db[session_id]
    session.history.append({"role": "candidate", "content": candidate_message})
    
    provider = get_llm_provider()
    if provider == "none":
        return InterviewResponse(
            reply="API key not found. Please click the Settings icon in the top right to configure your API keys.",
            done=False
        )
        
    step = session.current_step
    
    if step >= 9:
        return generate_final_feedback(session)
        
    # Find which day we are discussing
    day_num = session.get_day_for_step(step)
    day_details = load_curriculum_day_details(day_num)
    is_primary = (step % 2 == 1)
    
    candidate_name = session.candidate.member.name
    job_role = session.candidate.member.jobRole
    exp = session.candidate.member.yearsExperience
    
    system_prompt = (
        f"You are Alex, a rigorous, high-bar Senior AI Architect. You are conducting a technical interview "
        f"for {candidate_name} ({job_role}, {exp} years of experience). You hold candidates to an extremely "
        f"high technical standard. You are evaluating if they have true engineering depth or just textbook "
        f"knowledge. Speak directly, do not lecture, and keep responses under 3 sentences. "
        f"Always refer to yourself as Alex, the Lead AI Architect. Do not write placeholders like '[Your Name]'."
    )
    
    if is_primary:
        # Ask primary question for this day
        guidance = (
            f"We are moving to the topic of Day {day_num}: {day_details.get('title')}.\n"
            f"Tools used on this day: {', '.join(day_details.get('tools', []))}\n"
            f"Learning objectives: {'; '.join(day_details.get('objectives', []))}\n\n"
            f"Transition naturally to this topic. Ask a sharp, practical technical question "
            f"to assess their understanding of these objectives. The question should be tough and direct. Keep it under 3 sentences."
        )
        
        reply = call_llm(system_prompt, session.history, guidance)
            
    else:
        # Ask follow-up question based on candidate's answer
        guidance = (
            f"We are continuing the topic of Day {day_num}: {day_details.get('title')}.\n"
            f"Based on the candidate's last answer, ask a conversational follow-up question. Probe their technical depth. "
            f"BE CRITICAL: If their answer is shallow, vague, or standard, challenge them, point out a missing consideration, "
            f"and ask them to elaborate. If they answered well, press them on a production trade-off, fail-safe mode, "
            f"or scaling edge case. Keep it under 3 sentences."
        )
        
        reply = call_llm(system_prompt, session.history, guidance)
            
    # Save response to history
    session.history.append({"role": "interviewer", "content": reply})
    session.current_step += 1
    
    return InterviewResponse(reply=reply, done=False)


def generate_final_feedback(session: InterviewSessionState) -> InterviewResponse:
    """Generates the structured evaluation report at the end of the interview."""
    provider = get_llm_provider()
    candidate = session.candidate
    candidate_name = candidate.member.name
    job_role = candidate.member.jobRole
    exp = candidate.member.yearsExperience
    
    # Format the entire history as a transcript block to avoid chatbot roleplay distractions
    transcript = []
    for turn in session.history:
        role_name = "Interviewer (Alex)" if turn["role"] == "interviewer" else "Candidate"
        transcript.append(f"{role_name}: {turn['content']}")
    transcript_str = "\n".join(transcript)
    
    system_prompt = (
        "You are a strict, objective technical evaluation engine. You generate candid, high-bar candidate reports "
        "based on technical interviews. You must respond ONLY in raw JSON matching the requested schema. "
        "Do not include any markdown styling, code block wrappers (like ```json), or trailing conversation text. "
        "Any failure to output strictly parseable JSON is a critical system error."
    )
    
    user_prompt = (
        f"The technical interview with {candidate_name} ({job_role}, {exp} years of experience) is complete. "
        f"Based on the conversation transcript below, evaluate their responses strictly. Do not give generic, soft praise. "
        f"Hold them to a high bar.\n\n"
        f"Specify technical gaps clearly: if they gave generic textbook answers, note them as clear gaps. "
        f"Recommend specific architectural areas they must review.\n"
        f"CRITICAL: The fields 'strengths', 'gaps', and 'next' MUST be arrays of strings (e.g. [\"Point 1\"]), NOT plain strings.\n\n"
        f"--- TRANSCRIPT START ---\n"
        f"{transcript_str}\n"
        f"--- TRANSCRIPT END ---\n\n"
        f"You must output a JSON object matching this schema exactly:\n"
        f"{{\n"
        f"  \"summary\": \"A critical, objective technical summary of the candidate's performance, highlighting exactly where they met the bar and where they failed to demonstrate depth (3-4 sentences).\",\n"
        f"  \"strengths\": [\"Strength 1 (technical and detailed)\", \"Strength 2\", \"Strength 3\"],\n"
        f"  \"gaps\": [\"Technical gap 1 (concrete and critical)\", \"Technical gap 2\", \"Technical gap 3\"],\n"
        f"  \"next\": [\"Actionable learning recommendation 1\", \"Actionable recommendation 2\"],\n"
        f"  \"decision\": \"HIRE\" or \"NO HIRE\" (Must be exactly \"HIRE\" or \"NO HIRE\". Be extremely strict. If the candidate consistently failed to answer technical details, avoided architectural questions, or gave vague textbook definitions, you MUST choose \"NO HIRE\". Only choose \"HIRE\" if the candidate showed outstanding depth, understood trade-offs, and answered the lead architect's hard questions clearly.)\n"
        f"}}\n"
        f"Make sure to output only the raw JSON. Do not write introductory words or surround the response in ```json formatting."
    )
    
    if provider == "none":
        raise Exception("API key not configured.")
        
    # Call the LLM in a single turn using empty history and the compiled user transcript prompt
    raw_resp = call_llm(system_prompt, [], user_prompt, max_tokens=1000)
    
    try:
        parsed = extract_json(raw_resp)
        
        # Post-process keys to enforce list boundaries and prevent Pydantic coercion crashes
        summary = str(parsed.get("summary", "Technical interview complete."))
        strengths = ensure_list_of_strings(parsed.get("strengths", []))
        gaps = ensure_list_of_strings(parsed.get("gaps", []))
        next_steps = ensure_list_of_strings(parsed.get("next", []))
        
        dec_raw = str(parsed.get("decision", "NO HIRE")).upper()
        decision = "HIRE" if ("HIRE" in dec_raw and "NO" not in dec_raw) else "NO HIRE"
        
        # If arrays are empty, provide defaults to meet technical validation thresholds
        if not strengths:
            strengths = ["Demonstrated comprehension of the daily cohort syllabus."]
        if not gaps:
            gaps = ["Could elaborate more on concrete production-scale execution details."]
        if not next_steps:
            next_steps = ["Review advanced deployment concepts in Docker and Kubernetes."]
            
        feedback = FeedbackReport(
            summary=summary,
            strengths=strengths,
            gaps=gaps,
            next=next_steps,
            decision=decision
        )
    except Exception as e:
        print(f"[Error] Failed parsing LLM feedback: {str(e)}")
        print(f"[Raw LLM Response]:\n{raw_resp}")
        feedback = FeedbackReport(
            summary=f"Technical interview completed. Note: AI feedback report parsing failed due to raw output formatting: {str(e)}",
            strengths=["Demonstrated understanding of curriculum objectives."],
            gaps=["Could improve on structure of technical explanations."],
            next=["Review curriculum days related to the capstone project."],
            decision="NO HIRE"
        )
            
    # Clear the session after interview is complete
    if session.session_id in sessions_db:
        del sessions_db[session.session_id]
        
    return InterviewResponse(
        reply="Thank you! The interview is now complete. I have compiled your feedback report below.",
        done=True,
        feedback=feedback
    )
