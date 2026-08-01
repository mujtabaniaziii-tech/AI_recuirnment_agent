from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List
from pydantic import BaseModel
from ai_agent import (
    extract_text_from_pdf, 
    evaluate_resume, 
    generate_interview_questions, 
    get_available_slots,          # Naya function import kiya
    book_interview_slot,          # Naya function import kiya
    summarize_and_recommend
)

app = FastAPI(title="AI Recruitment Agent API")

@app.get("/")
def read_root():
    return {"message": "AI Recruitment Agent is running!"}

@app.post("/analyze-resumes/")
async def analyze_resumes(
    job_description: str = Form(...),
    files: List[UploadFile] = File(...)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    results = []
    for file in files:
        if not file.filename.endswith('.pdf'):
            results.append({"filename": file.filename, "error": "Only PDF files are supported."})
            continue

        try:
            file_bytes = await file.read()
            resume_text = extract_text_from_pdf(file_bytes)
            scorecard = evaluate_resume(job_description, resume_text)
            
            missing_skills = scorecard.get("missing_skills", [])
            questions_data = generate_interview_questions(job_description, missing_skills)
            
            scorecard["interview_questions"] = questions_data.get("interview_questions", [])
            scorecard["filename"] = file.filename
            
            results.append(scorecard)

        except Exception as e:
            results.append({"filename": file.filename, "error": str(e)})

    results.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
    return {"status": "success", "data": results}

# Data Models for extra features
class BookingRequest(BaseModel):
    candidate_email: str
    candidate_name: str
    slot_time: str

class FeedbackRequest(BaseModel):
    candidate_name: str
    job_description: str
    interview_notes: str

# Naya Endpoint: Google Calendar se free slots fetch karne ke liye
@app.get("/api/slots")
def fetch_slots():
    try:
        slots = get_available_slots()
        return {"available_slots": slots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Naya Endpoint: Google Meet link banana aur Calendar par event save karna
@app.post("/api/book-slot")
def book_slot(request: BookingRequest):
    try:
        result = book_interview_slot(request.candidate_email, request.candidate_name, request.slot_time)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize-interview/")
def summarize_interview(request: FeedbackRequest):
    try:
        summary_data = summarize_and_recommend(request.candidate_name, request.job_description, request.interview_notes)
        return {"status": "success", "data": summary_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))