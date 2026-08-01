# 🤖 AI Recruitment Agent

An intelligent, fully automated AI-driven recruitment application that streamlines the hiring process. This agent evaluates candidate resumes against job descriptions, scores them, and operates on an "Auto-Pilot" mode to automatically schedule Google Meet interviews for top candidates.

## 🌟 Key Features
* **Resume Parsing & Scoring:** Extracts text from PDF resumes and evaluates them against specific job descriptions using LLMs.
* **Skill Matching:** Automatically identifies matched and missing skills.
* **Auto-Pilot Mode:** Automatically selects the highest-scoring candidate and books the earliest available interview slot.
* **Google Workspace Integration:** Automatically creates Google Calendar events and generates Google Meet links for interviews.
* **Interview Prep:** Generates customized interview questions based on a candidate's missing skills.
* **Post-Interview Feedback:** Generates an automated hiring recommendation and summary based on interview notes.

## 🛠️ Tech Stack
* **Frontend:** Streamlit (Python)
* **Backend:** FastAPI (Python)
* **AI Model:** Google Gemini (1.5 Flash)
* **Integrations:** Google Calendar API, Google Meet API
* **Other Tools:** PyPDF2, pdfplumber

## ⚙️ Installation & Setup

Follow these steps to run the project on your local machine:

### 1. Prerequisites
* Python 3.9+ installed on your system.
* A Google Gemini API Key.
* Google Cloud Console account with **Google Calendar API** enabled (download your `credentials.json`).

### 2. Clone the Repository
```bash
git clone [https://github.com/mujtabaniaziii-tech/AI_recuirnment_agent.git](https://github.com/mujtabaniaziii-tech/AI_recuirnment_agent.git)
cd AI_recuirnment_agent
