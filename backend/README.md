# AI Recruitment Agent

An autonomous agent designed to streamline and handle the top of the hiring funnel. This project parses incoming resumes, ranks candidates against job requirements, generates tailored interview questions, automates interview scheduling, and provides post-interview summaries with hiring recommendations[cite: 1].

## 🚀 Key Features
* **Resume Parsing & Evaluation:** Extracts text from PDFs and scores candidates based on experience alignment and skill matching[cite: 1].
* **Tailored Interview Prep:** Automatically detects missing skills and generates custom technical interview questions[cite: 1].
* **Automated Scheduling:** Drafts professional interview invitation emails and generates mock calendar booking links[cite: 1].
* **Post-Interview Summaries & Recommendations:** Evaluates interview feedback to produce a structured summary, strengths, weaknesses, and a final "Hire / No-Hire" recommendation[cite: 1].

---

## 🛠️ Tech Stack
* **Backend:** FastAPI, Python, Google Gemini API (`gemini-3.6-flash`), PyPDF2
* **Frontend:** Streamlit
* **Architecture:** Modular Agentic Workflow (Pipeline-based processing)

---

## 📂 Project Structure
```text
AI_recuirnment_agent/
│
├── backend/
│   ├── ai_agent.py      # Core AI logic & Gemini integration
│   ├── main.py          # FastAPI endpoints
│   └── .env             # API Key configuration
│
├── frontend/
│   └── app.py           # Streamlit user interface
│
└── README.md