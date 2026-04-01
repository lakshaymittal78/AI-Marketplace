# OneAgent — AI Marketplace Platform

> Describe a task. It gets done.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent_Orchestration-FF6B35?style=flat)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70b-F55036?style=flat)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Cloud-336791?style=flat&logo=postgresql&logoColor=white)
![Railway](https://img.shields.io/badge/Deployed-Railway-0B0D0E?style=flat&logo=railway&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

**OneAgent** is a deployed, full-stack AI platform that routes natural language requests to specialized agents — automatically. No dropdowns. No mode switching. Just describe what you need.

🔗 **[Live Demo](https://your-frontend-url.railway.app)** · **[API Docs](https://your-backend-url.railway.app/docs)** · **[Frontend Repo](https://github.com/lakshaymittal78/AI-Marketplace-Frontend)**

---

## What It Does

Type naturally. The agent figures out the rest.

| Input | Agent | What Happens |
|-------|-------|--------------|
| `"write a function to reverse a linked list"` | **Code Agent** | Plans → writes → reviews → rewrites → returns clean code |
| `"find latest news on OpenAI and summarize it"` | **Search Agent** | Pulls live results, condenses into a summary |
| `"make a 5-slide deck about climate change"` | **PPT Agent** | Generates and returns a `.pptx` file |
| `"generate an image of a futuristic city"` | **Image Agent** | Returns a direct image link |
| `"send an email to john@company.com about the meeting"` | **Email Agent** | Drafts and sends via Gmail SMTP |
| `"hey, what's the capital of France?"` | **Chat Agent** | Responds conversationally |

---

## Architecture

```
User Input (Natural Language)
          │
          ▼
    FastAPI Backend
          │
          ▼
   LangGraph Router          ← classifies intent
          │
    ┌─────┼──────┬────────┬────────┬────────┐
    ▼     ▼      ▼        ▼        ▼        ▼
  Chat  Code  Search   Image    PPT     Email
 Agent Agent  Agent   Agent   Agent   Agent
          │
     ReAct Loop
   plan → write
   review → rewrite
          │
          ▼
    Final Response
          │
          ▼
  PostgreSQL (usage tracking + auth)
```

---

## The Code Agent — ReAct Loop

Most AI tools give a one-shot answer. The Code Agent is different.

```
Step 1: READ      → Understands the problem, identifies edge cases
Step 2: PLAN      → Outlines approach before writing a single line
Step 3: WRITE     → Generates the implementation
Step 4: REVIEW    → Critiques its own output
Step 5: REWRITE   → Fixes issues if found
Step 6: RETURN    → Delivers clean, final code
```

The result: code with **type hints, error handling, and test cases** — not just a bare function.

---

## Stack

### Backend
- **FastAPI** — async REST API framework
- **LangGraph** — agent state machine and orchestration
- **Groq (LLaMA 3.3-70b)** — LLM inference
- **PostgreSQL** — cloud-hosted database (Railway)
- **SQLAlchemy** — ORM and database modeling
- **JWT** — authentication and route protection
- **Usage tracking** — per-user request monitoring

### Frontend
- **React + Vite** — fast SPA setup
- **Tailwind CSS** — utility-first styling
- **Framer Motion** — smooth animations

### Agents & Tools
- **Chat** — Groq LLaMA conversational agent
- **Code** — ReAct pipeline (plan → write → review → rewrite)
- **Search** — DuckDuckGo live web search
- **Image** — Pollinations text-to-image
- **PPT** — python-pptx file generation
- **Email** — Gmail SMTP integration

### Deployment
- **Railway** — backend + frontend + PostgreSQL, all live

---

## Project Structure

```
AI-Marketplace-Backend/
├── OneAgent/
│   ├── main.py                  # FastAPI app entry point
│   └── app/
│       ├── agent/
│       │   ├── graph.py         # LangGraph state machine
│       │   ├── router.py        # Intent classification → tool dispatch
│       │   └── tools/
│       │       ├── chat.py
│       │       ├── code.py      # ReAct loop implementation
│       │       ├── search.py
│       │       ├── image.py
│       │       ├── ppt.py
│       │       └── email.py
│       ├── routers/             # FastAPI route handlers
│       ├── models/              # SQLAlchemy models
│       └── utils/               # Shared utilities
├── railpack.toml                # Railway deployment config
├── .gitignore
└── README.md
```

---

## Local Setup

### Prerequisites
- Python 3.11+
- PostgreSQL (local or cloud)
- Groq API key — [get one free](https://console.groq.com)

### Backend

```bash
cd OneAgent
python -m venv .venv

# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_key
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your_jwt_secret
EMAIL_ADDRESS=your_gmail@gmail.com
EMAIL_PASSWORD=your_app_password
```

```bash
uvicorn main:app --reload
```

API docs available at: `http://localhost:8000/docs`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login, returns JWT token |
| `POST` | `/agent/run` | Send a task to the agent router |
| `GET` | `/agent/history` | Get past agent interactions |
| `GET` | `/health` | Health check |

---

## Key Design Decisions

**Why LangGraph over plain LangChain?**
LangGraph gives explicit control over agent state transitions. Every node in the graph has a defined role — router, tool executor, response formatter. This makes the system debuggable and extensible, not a black box.

**Why Groq?**
LLaMA 3.3-70b on Groq runs at ~500 tokens/second. For a ReAct loop that makes multiple inference calls per request, latency matters. Groq keeps the Code Agent fast enough to be usable.

**Why separate repos for frontend and backend?**
Independent deployment cycles. The backend can be updated, redeployed, and scaled without touching the frontend — and vice versa.

---

## Roadmap

- [ ] RAG pipeline — upload documents, query them with agents
- [ ] WebSocket streaming — stream agent responses token by token
- [ ] Celery + Redis — background task queue for long-running agents
- [ ] LangSmith observability — trace every agent step
- [ ] Multi-tenant support — team workspaces

---

## Author

**Lakshay Mittal** — AI Engineer Intern @ Netsmartz

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat&logo=linkedin)](https://linkedin.com/in/your-profile)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat&logo=github)](https://github.com/lakshaymittal78)

---

## License

MIT — use it, learn from it, build on it.
