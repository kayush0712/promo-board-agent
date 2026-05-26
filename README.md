# 🤖 Agentic Promotion Review Board

An autonomous, multi-agent backend system built using FastAPI, MongoDB, and Large Language Models (LLMs) to evaluate employee promotion packets with structured reasoning and human oversight.

Instead of relying on a single AI prompt, this platform uses a swarm-style multi-agent architecture where specialized AI agents collaborate, debate, validate evidence, and generate promotion recommendations grounded in real employee performance data.

---

# 🧠 Multi-Agent Architecture

The review pipeline consists of 5 specialized AI agents:

| Agent | Responsibility |
|---|---|
| **Harvester** | Collects raw employee metrics from multiple systems |
| **Advocate** | Builds the strongest possible case for promotion |
| **Evaluator** | Critically evaluates evidence against competency expectations |
| **Sentinel** | Validates compensation feasibility and policy constraints |
| **Orchestrator** | Synthesizes all agent outputs into a final recommendation |

---

## 🔍 Reflection Loop (Evaluator)

The Evaluator agent contains an autonomous reflection loop capable of:

- detecting missing evidence
- requesting additional context
- rerunning evaluations
- improving confidence scoring

This prevents shallow or hallucinated promotion decisions.

---

# ✨ Key Technical Features

## ⚡ Real-Time SSE Streaming

Streams live agent execution updates to the frontend using:

- Server-Sent Events (SSE)
- async FastAPI streaming
- live orchestration tracing

Example live updates:

```text
[HARVESTER] Collecting metrics...
[ADVOCATE] Building promotion case...
[EVALUATOR] Detecting evidence gaps...
[SENTINEL] Validating compensation band...
```

---

## 🛡️ Prompt Injection Protection

Implements XML-style prompt fencing to isolate trusted instructions from untrusted employee-generated content.

Example:

```xml
<employee_metrics>
...
</employee_metrics>
```

Prevents indirect prompt injection attacks from:
- Jira tickets
- Slack messages
- GitHub comments
- peer reviews

---

## 🔄 Stateful Crash Recovery

Implements a Cache-Aside recovery strategy using MongoDB.

If the server crashes during evaluation:
- sessions are restored automatically
- review progress is recovered
- final state remains persistent

---

## 🧠 Autonomous AI Safety Controls

Built-in safeguards include:

- max reflection loop ceilings
- token usage tracking
- structured JSON validation
- deterministic fallback handling
- confidence-based review logic

---

## 👨‍💼 Human-in-the-Loop Approval

The system is intentionally designed as a:

> decision-support platform

—not a fully autonomous decision-maker.

Managers can:
- approve recommendations
- reject promotions
- request additional evidence

before final HR action.

---

# 🛠️ Tech Stack

## Backend
- Python 3.9+
- FastAPI
- Uvicorn
- AsyncIO

## Database
- MongoDB
- Motor (async MongoDB driver)

## AI Infrastructure
- Groq API
- OpenRouter API
- LLM orchestration pipelines

## Validation & Security
- Pydantic
- API Key authentication
- XML prompt fencing

## Frontend
- Streamlit (real-time orchestration dashboard)

---

# 📁 Recommended Folder Structure

```text
project/
│
├── app.py
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── orchestrator.py
│   ├── models.py
│   ├── database.py
│   ├── mock_data.py
│   │
│   └── agents/
│       ├── __init__.py
│       ├── base.py
│       ├── harvester.py
│       ├── advocate.py
│       ├── evaluator.py
│       ├── sentinel.py
│       └── orchestrator_agent.py
│
├── requirements.txt
├── .env
└── README.md
```

---

# ⚙️ Installation & Setup

## 1. Clone Repository

```bash
git clone https://github.com/kayush0712/promo-board-agent.git
cd promo-board-agent
```

---

## 2. Create Virtual Environment

### macOS/Linux

```bash
python -m venv venv
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file in the project root:

```env
# Internal API Authentication
INTERNAL_API_KEY=your_super_secret_key

# MongoDB
MONGO_URL=mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=promotion_review

# LLM Providers
GROQ_API_KEY=your_groq_api_key
OPENROUTER_API_KEY=your_openrouter_key
```

---

# 🚀 Running the Backend

Start FastAPI server:

```bash
uvicorn backend.main:app --reload --port 8000
```

API available at:

```text
http://localhost:8000
```

Swagger Docs:

```text
http://localhost:8000/docs
```

---

# 🖥️ Running the Streamlit Frontend

Start Streamlit dashboard:

```bash
streamlit run app.py
```

Frontend available at:

```text
http://localhost:8501
```

---

# 🔌 Core API Endpoints

All endpoints require:

```text
X-API-Key
```

header authentication.

---

## Start Review

```http
POST /review/{employee_id}
```

Starts the multi-agent pipeline and streams live SSE updates.

---

## Review Status

```http
GET /status/{employee_id}
```

Returns current review state from RAM or MongoDB.

---

## Human Decision

```http
POST /decide/{employee_id}
```

Accepts manager approval/rejection.

---

## Review History

```http
GET /history
```

Returns latest review summaries.

---

## Employee Review History

```http
GET /history/{employee_id}
```

Returns full persisted review packet.

---

# 📡 Example SSE Event

```json
{
  "agent": "evaluator",
  "status": "running",
  "message": "Cross-checking evidence against competency matrix..."
}
```

---

# 🔒 Security Features

- API key authentication
- Prompt injection protection
- XML prompt fencing
- Structured JSON parsing
- Token usage monitoring
- Async queue protection
- Rate-safe streaming buffers

---

# 🧪 Future Improvements

- JWT authentication
- RBAC permissions
- Langfuse observability
- Distributed async workers
- Redis queue integration
- Vector database retrieval
- Automated evaluation benchmarks
- Bias detection pipelines

---

# 🎯 Why This Project Matters

This project demonstrates:

- multi-agent orchestration
- enterprise AI workflows
- autonomous reasoning loops
- structured LLM evaluation
- production-aware backend engineering
- human-in-the-loop governance

It is designed to simulate how real AI-assisted enterprise decision systems may operate in production environments.

---

# 👨‍💻 Author

Built by Ayush Kumar

Second-year B.Tech student focused on:
- AI systems
- agentic workflows
- backend engineering
- LLM orchestration
\
