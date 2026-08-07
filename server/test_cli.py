import json
import requests
import sys

# Test script for end-to-end interview flow validation

BASE_URL = "http://localhost:8000"

def test_full_flow():
    # 1. Fetch a candidate to test with
    print("[-] Fetching candidates list...")
    try:
        resp = requests.get(f"{BASE_URL}/api/candidates")
        resp.raise_for_status()
        candidates = resp.json().get("candidates", [])
        if not candidates:
            print("[x] Error: No candidates found.")
            sys.exit(1)
        candidate = candidates[0]
        print(f"[✓] Found candidate: {candidate['member']['name']} ({candidate['member']['id']})")
    except Exception as e:
        print(f"[x] Failed to connect to server: {str(e)}")
        print("    Ensure uvicorn is running on port 8000 first (./run.sh)")
        sys.exit(1)

    # 2. Start the interview
    session_id = "test-cli-session-789"
    print(f"[-] Initializing interview session {session_id}...")
    start_payload = {
        "sessionId": session_id,
        "candidate": candidate
    }
    
    resp = requests.post(f"{BASE_URL}/api/interview", json=start_payload)
    resp.raise_for_status()
    data = resp.json()
    print(f"[Interviewer]: {data['reply']}\n")

    # 3. Simulate turns (8 questions total)
    # We will send standard technical responses containing keywords
    answers = [
        "Yes, I am ready to begin the interview. Let's start.",
        "Lexical search matches exact terms like keywords, while semantic search uses embeddings to represent text meanings in high-dimensional vector space, allowing it to capture query intents and synonyms.",
        "Cosine similarity measures the angle between vector embeddings, finding the cosine of the angle between them. If they point in similar directions, they are semantically similar. For cold weather, it maps to similar dimensions.",
        "A vector database is optimized for multi-dimensional similarity search and indexing, whereas relational databases like PostgreSQL struggle to search high-dimensional vectors efficiently without extensions.",
        "For small datasets, pgvector on Postgres is great to avoid infrastructure complexity. But for huge vector scales, a dedicated database like Pinecone or Qdrant is preferred for better indexing speeds and search latency.",
        "Prompt engineering uses techniques like system instructions, few-shot prompt examples, or Chain-of-Thought reasoning to guide the LLM's outputs and prevent hallucinations.",
        "I structured my system instructions to strictly constrain the model, instructing it to only answer questions using the retrieved search documents, and reply that it does not know if info is missing.",
        "LangChain agents use a ReAct framework loop to dynamically select and execute tools based on user queries, whereas a static LangChain chain is a pre-defined sequence of calls.",
        "A ReAct loop works by having the agent output its Thought, select an Action tool, read the Observation result, and repeat until the final answer is reached."
    ]

    for idx, ans in enumerate(answers):
        print(f"[Candidate]: {ans}")
        payload = {
            "sessionId": session_id,
            "message": ans
        }
        resp = requests.post(f"{BASE_URL}/api/interview", json=payload)
        resp.raise_for_status()
        data = resp.json()
        print(f"[Interviewer]: {data['reply']}\n")
        
        # Check if completed
        if data.get("done"):
            print("[✓] Interview successfully completed!")
            print("[-] Structured Feedback Summary:")
            feedback = data.get("feedback", {})
            print(json.dumps(feedback, indent=2))
            return
            
    print("[x] Error: Interview did not complete after all turns.")
    sys.exit(1)

if __name__ == "__main__":
    test_full_flow()
