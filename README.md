# AI-Marketplace
OneAgent
You describe a task. It gets done.
OneAgent is an AI platform that figures out what you're trying to do and picks the right tool automatically — whether that's writing code, searching the web, generating an image, building a presentation, or sending an email.
What it does
Type naturally. The agent handles the rest.

"write a function to reverse a linked list" → Code Agent plans, writes, and reviews the solution
"find latest news on OpenAI and summarize it" → Search Agent pulls results and condenses them
"make a 5-slide deck about climate change" → PPT Agent generates and saves a .pptx file
"generate an image of a futuristic city" → Image Agent returns a direct image link
"send an email to john@company.com about the meeting" → Email Agent drafts and sends it

Stack
Backend

FastAPI + PostgreSQL + SQLAlchemy
LangGraph for agent orchestration
Groq (llama-3.3-70b) for inference
JWT auth, usage tracking

Frontend

React + Tailwind + Framer Motion
Vite

Agents

Chat, Code (ReAct pipeline), Search (DuckDuckGo), Image (Pollinations), PPT (python-pptx), Email (Gmail SMTP)

How the Code Agent works differently
Most AI tools give you a one-shot answer. The Code Agent runs a ReAct loop:

Reads the problem and makes a plan
Writes the code
Reviews its own output
Rewrites if something's off
Returns a final, cleaned-up answer

The difference shows. You get type hints, error handling, and test cases — not just a bare function.
Setup
bash# backend
cd OneAgent
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# add your keys to .env
GROQ_API_KEY=...
DATABASE_URL=postgresql://...
SECRET_KEY=...
EMAIL_ADDRESS=...
EMAIL_PASSWORD=...

uvicorn main:app --reload
bash# frontend
cd marketplace
npm install
npm run dev
Project structure
OneAgent/
├── main.py
├── app/
│   ├── agent/
│   │   ├── graph.py       # LangGraph state machine
│   │   ├── router.py      # decides which tool to use
│   │   └── tools/
│   │       ├── chat.py
│   │       ├── code.py
│   │       ├── search.py
│   │       ├── image.py
│   │       ├── ppt.py
│   │       └── email.py
│   ├── routers/
│   ├── models/
│   └── utils/

marketplace/
├── src/
│   ├── pages/
│   ├── components/
│   └── utils/api.ts
