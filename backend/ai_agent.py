import os
import io
import json
import re
import datetime
import PyPDF2
import pdfplumber
import google.generativeai as genai
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ==========================================
# 1. SETUP GEMINI API
# ==========================================
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in the .env file")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3.6-flash', generation_config={"response_mime_type": "application/json"})

# ==========================================
# 2. BULLETPROOF JSON EXTRACTOR
# ==========================================
def extract_json_from_text(raw_text):
    """AI ke jawab mein se sirf kaam ka JSON nikalta hai aur extra code blocks hata deta hai"""
    try:
        # Regex se sirf JSON object {...} nikalna
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(raw_text)
    except Exception as e:
        raise ValueError(f"AI Response Format Error: {e}")

# ==========================================
# 3. GEMINI AI FUNCTIONS (RESUME & INTERVIEW)
# ==========================================
def extract_text_from_pdf(file_bytes):
    text = ""
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception:
        pass
        
    if not text.strip():
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e:
            raise ValueError(f"Could not read PDF file: {e}")
            
    return text

def evaluate_resume(job_description, resume_text):
    prompt = f"""
    You are an expert technical recruiter. Analyze the resume against the job description.
    Output exactly this JSON structure and nothing else:
    {{
        "candidate_name": "Extract from resume if possible, else 'Unknown'",
        "candidate_email": "Extract email address from resume if possible, else ''",
        "overall_score": 85,
        "matched_skills": ["skill1", "skill2"],
        "missing_skills": ["skill3", "skill4"],
        "experience_alignment": "Brief summary of how experience matches."
    }}
    Job Description: {job_description}
    Resume Text: {resume_text}
    """
    response = model.generate_content(prompt)
    return extract_json_from_text(response.text)

def generate_interview_questions(job_description, missing_skills):
    skills_text = ", ".join(missing_skills) if missing_skills else "None"
    prompt = f"""
    You are an expert technical interviewer. Based on the job description and missing skills, 
    generate 3 targeted interview questions.
    Output exactly this JSON structure:
    {{
        "interview_questions": ["Question 1", "Question 2", "Question 3"]
    }}
    Job Description: {job_description}
    Missing Skills: {skills_text}
    """
    response = model.generate_content(prompt)
    return extract_json_from_text(response.text)

def summarize_and_recommend(candidate_name, job_description, interview_notes):
    prompt = f"""
    You are an Expert Technical Hiring Manager. Provide a concise summary and hiring recommendation.
    Output exactly this JSON structure:
    {{
        "interview_summary": "A 2-3 sentence summary.",
        "strengths": ["strength1", "strength2"],
        "weaknesses": ["weakness1", "weakness2"],
        "final_recommendation": "Hire", 
        "justification": "Why this recommendation is made."
    }}
    Candidate: {candidate_name}
    Job: {job_description}
    Notes: {interview_notes}
    """
    response = model.generate_content(prompt)
    return extract_json_from_text(response.text)

# ==========================================
# 4. GOOGLE CALENDAR & MEET INTEGRATION
# ==========================================
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    if not os.path.exists('token.json'):
        raise Exception("token.json file nahi mili. Pehle test_calendar.py run karein.")
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    return build('calendar', 'v3', credentials=creds)

def get_available_slots():
    service = get_calendar_service()
    now = datetime.datetime.utcnow()
    time_min = now.isoformat() + 'Z'
    time_max = (now + datetime.timedelta(days=3)).isoformat() + 'Z'

    body = {"timeMin": time_min, "timeMax": time_max, "items": [{"id": "primary"}]}
    freebusy_result = service.freebusy().query(body=body).execute()
    busy_slots = freebusy_result['calendars']['primary']['busy']

    available_slots = []
    for day in range(3):
        target_date = now + datetime.timedelta(days=day)
        for hour in [10, 14, 16]:
            slot_time = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            if slot_time > now:
                slot_str = slot_time.strftime("%Y-%m-%d %H:%M")
                is_busy = False
                slot_start_iso = slot_time.isoformat() + 'Z'
                for busy in busy_slots:
                    if busy['start'] <= slot_start_iso <= busy['end']:
                        is_busy = True
                        break
                if not is_busy:
                    available_slots.append(slot_str)
    return available_slots[:5]

def book_interview_slot(candidate_email, candidate_name, slot_time_str):
    service = get_calendar_service()
    start_time = datetime.datetime.strptime(slot_time_str, "%Y-%m-%d %H:%M")
    end_time = start_time + datetime.timedelta(minutes=30)
    
    event = {
        'summary': f'Interview with {candidate_name} - AI Recruitment',
        'description': f'Automated interview scheduling for candidate: {candidate_email}',
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Karachi'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Asia/Karachi'},
        'attendees': [{'email': candidate_email}],
        'conferenceData': {
            'createRequest': {'requestId': f"interview_{int(datetime.datetime.now().timestamp())}", 'conferenceSolutionKey': {'type': 'hangoutsMeet'}}
        },
        'reminders': {'useDefault': False, 'overrides': [{'method': 'email', 'minutes': 24 * 60}, {'method': 'popup', 'minutes': 10}]},
    }
    event_result = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1, sendUpdates='all').execute()
    return {"status": "Success", "meet_link": event_result.get('hangoutLink'), "html_link": event_result.get('htmlLink')}