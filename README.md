# ABTalks AI Cohort · Interviewer Agent

A premium, state-of-the-art AI Technical Interviewer Agent built for the ABTalks AI Cohort. The agent conducts realistic, candidate-specific, multi-turn technical interviews based on their curriculum progress and outputs structured technical evaluation reports.

## Features

- **Conversational State Machine**: Conducts a multi-turn conversation with at least 8 questions covering at least 4 curriculum days.
- **Candidate-Specific Customization**: Analyzes candidate experience, education, and cohort completion signals to adjust questions.
- **Dynamic Follow-Ups**: Probes candidate depth, asks clarifying questions for vague answers, or challenges them with edge cases.
- **Evaluation & Feedback**: Generates structured reports containing performance summaries, strengths, technical gaps, and recommended next steps.
- **API Spec Compliant**: Fully implements the contract defined in the Technical Specification (`POST /api/interview`).
- **Interactive UI Dashboard**: Premium dark-mode glassmorphic interface showing candidates list, their mission status timeline, live chat, progress tracking, and detailed report rendering.
- **Multi-Model Provider Support**: Plugs into Gemini API, OpenAI API, or runs in a robust stateful Mock Simulator fallback mode when API keys are not supplied.

## Project Structure

```
interview-agent/
├── data/
│   ├── candidates.json       # Candidate profiles
│   ├── curriculum.json       # AI cohort daily syllabus
│   └── technical-spec.md     # Endpoint contract spec
├── server/
│   ├── __init__.py
│   ├── main.py               # FastAPI server & static file server
│   ├── models.py             # Pydantic request/response models
│   ├── agent.py              # LLM prompt routing & state machine
│   └── questions_db.py       # Fallback curriculum questions
├── static/
│   ├── index.html            # Main dashboard HTML template
│   ├── styles.css            # Dark mode glassmorphic styling
│   └── app.js                # Frontend controllers & state
├── .env                      # Configuration file (API keys)
├── requirements.txt          # Python packages
├── run.sh                    # Server startup script
└── README.md                 # Documentation
```

## Setup & Running

1. **Activate the Virtual Environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Start the Server**:
   ```bash
   ./run.sh
   ```
   The server runs locally at [http://localhost:8000](http://localhost:8000).

3. **Accessing the Dashboard**:
   Open your browser and navigate to [http://localhost:8000](http://localhost:8000) to select a candidate and start their interview.

4. **Configuring AI Models**:
   Click the **Settings** button in the top-right of the dashboard to save your `GEMINI_API_KEY` or `OPENAI_API_KEY`. Alternatively, set them in the `.env` file directly:
   ```env
   GEMINI_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ```
   If no keys are provided, the server runs in a highly realistic **Mock Simulator Mode** allowing you to test and demo the entire application flow out-of-the-box.
