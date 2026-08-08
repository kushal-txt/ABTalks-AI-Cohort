# ABTalks AI Cohort · Technical Interviewer Agent

A premium, state-of-the-art AI Technical Interviewer Agent built for the ABTalks AI Cohort. The agent conducts realistic, candidate-specific, multi-turn technical interviews based on their curriculum progress and outputs structured technical evaluation reports with a final hire verdict.

## 🚀 Live Demo & Deployment
- **Production URL**: [https://ab-talks-ai-cohort.vercel.app/](https://ab-talks-ai-cohort.vercel.app/)
- **Vercel Serverless Hosting**: Built using a zero-config Python ASGI entrypoint, caching static assets at the Edge CDN and processing conversation turns via serverless functions.

---

## ✨ Features

- **Conversational State Machine**: Conducts a multi-turn conversation with exactly 8 questions covering at least 4 curriculum days.
- **Strict Interviewer Persona**: Powered by a demanding technical lead persona ("Alex, Lead AI Architect") that challenges shallow or copy-paste textbook definitions and probes for production-ready designs.
- **Secure API Key Management**: Configuration dashboard allows saving custom OpenRouter, Gemini, or OpenAI credentials. Keys are saved privately in `.env` and can be dynamically deleted to prevent extra charges.
- **Robust Fail-Safe JSON Parser**: Includes automatic key fallback rotation (primary & secondary API keys), retries with exponential backoff, and a regex-based JSON extractor with Pydantic coercion fallback to prevent validation failures.
- **Hiring Verdict Stamp**: The evaluation report concludes with a strict **`HIRE`** or **`NO HIRE`** verdict badge, rendered in highly responsive Neo-Brutalist green/red indicators.
- **XSS Sanitization & DOM Security**: Frontend parses markdown blocks and safely encodes all client inputs and LLM outputs, eliminating script injection and XSS vectors.

---

## 📂 Project Structure

```
interview-agent/
├── api/
│   └── index.py              # Vercel Serverless entrypoint
├── data/
│   ├── candidates.json       # Candidate profiles
│   ├── curriculum.json       # AI cohort daily syllabus
│   └── technical-spec.md     # Endpoint contract spec
├── server/
│   ├── __init__.py
│   ├── main.py               # FastAPI server & route handlers
│   ├── models.py             # Pydantic request/response schemas
│   ├── agent.py              # LLM prompt routing & state machine
│   └── questions_db.py       # Helper curriculum descriptors
├── static/
│   ├── index.html            # Main dashboard HTML template
│   ├── styles.css            # Neo-Brutalist matte-grey theme
│   └── app.js                # Frontend controllers & state (XSS sanitized)
├── .env                      # Local secret variables (ignored by Git)
├── vercel.json               # Serverless bundling & routing configuration
├── requirements.txt          # Python packages (including requests)
├── run.sh                    # Server startup script
└── README.md                 # Project documentation
```

---

## 🛠️ Setup & Running

### Option 1: Local Development
1. **Activate the Virtual Environment**:
   ```bash
   source venv/bin/activate
   ```
2. **Configure API Keys**:
   Create a `.env` file in the root directory:
   ```env
   OPENROUTER_API_KEY=your_primary_key
   OPENROUTER_API_KEY_FALLBACK=your_secondary_key
   OPENROUTER_MODEL=google/gemini-2.5-flash
   ```
3. **Start the Server**:
   ```bash
   ./run.sh
   ```
   The dashboard will be active locally at [http://localhost:8000](http://localhost:8000).

### Option 2: Deploy to Vercel
This project is configured for **Vercel Serverless Functions** out-of-the-box.
1. Run `npx vercel` to link your project.
2. Add your environment variables (`OPENROUTER_API_KEY`, etc.) inside the Vercel Project Settings.
3. Deploy to production using:
   ```bash
   npx vercel --prod
   ```

---

## 📄 API Specification Compliant
Fully satisfies the contract specified in [`data/technical-spec.md`](file:///home/kiyo/interview-agent/data/technical-spec.md).

#### Start Interview
- **Endpoint**: `POST /api/interview`
- **Request Body**:
  ```json
  {
    "sessionId": "session-123",
    "candidate": { ... candidate profile ... }
  }
  ```

#### Progress Conversation
- **Endpoint**: `POST /api/interview`
- **Request Body**:
  ```json
  {
    "sessionId": "session-123",
    "message": "My answer to the prompt..."
  }
  ```
