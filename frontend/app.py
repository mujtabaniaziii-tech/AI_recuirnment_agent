import streamlit as st
import requests

# Page Configuration
st.set_page_config(page_title="AI Recruitment Agent", page_icon="🤖", layout="wide")
st.title("🤖 AI Recruitment Agent")
st.write("Upload resumes, evaluate candidates, and let AI automatically hire the best one!")

API_URL = "http://127.0.0.1:8000"

tab1, tab2, tab3 = st.tabs(["📄 Auto-Pilot Analysis", "📅 Manual Schedule", "📝 Interview Feedback"])

if 'analyzed_candidates' not in st.session_state:
    st.session_state['analyzed_candidates'] = {}

# ==========================================
# TAB 1: RESUME ANALYSIS & AUTO-PILOT
# ==========================================
with tab1:
    st.header("Resume Analysis & Scoring")
    job_description = st.text_area("Job Description", height=150, placeholder="Paste the job description here...")
    uploaded_files = st.file_uploader("Upload Candidate Resumes (PDF)", type=["pdf"], accept_multiple_files=True)
    
    # 🤖 AUTO-PILOT CHECKBOX
    st.markdown("---")
    auto_pilot = st.checkbox("🤖 Enable Auto-Pilot (Automatically find highest score and book interview)", value=True)
    
    if st.button("🚀 Analyze & Process Resumes"):
        if not job_description or not uploaded_files:
            st.warning("Please provide both Job Description and at least one Resume.")
        else:
            with st.spinner("Analyzing resumes with Gemini AI..."):
                files_data = [("files", (file.name, file.getvalue(), "application/pdf")) for file in uploaded_files]
                response = requests.post(f"{API_URL}/analyze-resumes/", data={"job_description": job_description}, files=files_data)
                
                if response.status_code == 200:
                    results = response.json().get("data", [])
                    st.success("Analysis Complete!")
                    
                    valid_candidates = []
                    
                    # Pehle sabko display karein aur valid candidates ko list mein dalen
                    for res in results:
                        if "error" in res:
                            st.error(f"❌ Could not process '{res.get('filename')}'. Error: {res.get('error')}")
                            continue
                        
                        name = res.get('candidate_name', 'Unknown')
                        email = res.get('candidate_email', '')
                        score = res.get('overall_score', 0)
                        
                        if name != 'Unknown' and email:
                            valid_candidates.append({"name": name, "email": email, "score": score})
                            st.session_state['analyzed_candidates'][f"{name} ({email})"] = {"name": name, "email": email}

                        st.subheader(f"Candidate: {name} ({res.get('filename')})")
                        if email:
                            st.caption(f"📧 **Email:** {email}")
                        st.write(f"**Score:** {score}/100")
                        st.write(f"**Matched Skills:** {', '.join(res.get('matched_skills', []))}")
                        st.write(f"**Missing Skills:** {', '.join(res.get('missing_skills', []))}")
                        st.write(f"**Experience Alignment:** {res.get('experience_alignment', '')}")
                        
                        with st.expander("Suggested Interview Questions"):
                            for q in res.get("interview_questions", []):
                                st.write(f"- {q}")
                        st.divider()

                    # 🤖 AUTO-PILOT LOGIC (Sab se zyada score wale ko dhondna aur book karna)
                    if auto_pilot and valid_candidates:
                        st.markdown("### 🤖 Auto-Pilot Activated")
                        # Sab se zyada score wala candidate nikalein
                        best_candidate = max(valid_candidates, key=lambda x: x['score'])
                        st.info(f"🏆 Top Candidate Found: **{best_candidate['name']}** with Score: {best_candidate['score']}/100")
                        
                        with st.spinner("Fetching slots and booking meeting automatically..."):
                            slots_res = requests.get(f"{API_URL}/api/slots")
                            if slots_res.status_code == 200:
                                slots = slots_res.json().get("available_slots", [])
                                if slots:
                                    first_slot = slots[0] # Sab se pehla free slot pick karein
                                    payload = {
                                        "candidate_name": best_candidate['name'],
                                        "candidate_email": best_candidate['email'],
                                        "slot_time": first_slot
                                    }
                                    book_res = requests.post(f"{API_URL}/api/book-slot", json=payload)
                                    
                                    if book_res.status_code == 200:
                                        data = book_res.json().get("data", {})
                                        st.success(f"✅ AUTOMATION SUCCESS: Interview booked for {best_candidate['name']} at {first_slot}!")
                                        st.markdown(f"**Google Meet Link:** [Join Meeting Here]({data.get('meet_link')})")
                                    else:
                                        st.error("Failed to auto-book the interview.")
                                else:
                                    st.warning("No free slots available on your calendar to auto-book.")
                            else:
                                st.error("Failed to connect to Google Calendar.")

                else:
                    st.error("Error analyzing resumes. Make sure the backend is running.")

# ==========================================
# TAB 2: MANUAL GOOGLE CALENDAR SCHEDULING
# ==========================================
with tab2:
    st.header("Manual Interview Scheduling")
    st.write("If you disabled Auto-Pilot, you can manually book an interview here.")
    if st.session_state['analyzed_candidates']:
        candidate_options = list(st.session_state['analyzed_candidates'].keys())
        selected_cand_label = st.selectbox("Select Candidate", candidate_options)
        candidate_name = st.session_state['analyzed_candidates'][selected_cand_label]['name']
        candidate_email = st.session_state['analyzed_candidates'][selected_cand_label]['email']
    else:
        col1, col2 = st.columns(2)
        with col1:
            candidate_name = st.text_input("Candidate Name", key="sched_name")
        with col2:
            candidate_email = st.text_input("Candidate Email", key="sched_email")
    
    if st.button("📅 Fetch Available Slots"):
        with st.spinner("Fetching free slots..."):
            res = requests.get(f"{API_URL}/api/slots")
            if res.status_code == 200:
                slots = res.json().get("available_slots", [])
                st.session_state['slots'] = slots
                if not slots:
                    st.warning("No free slots available.")
            else:
                st.error("Failed to fetch slots.")
                
    if 'slots' in st.session_state and st.session_state['slots']:
        selected_slot = st.selectbox("Select an Interview Slot", st.session_state['slots'])
        if st.button("✉️ Confirm Booking & Send Invite"):
            if not candidate_name or not candidate_email:
                st.warning("Please select candidate details.")
            else:
                with st.spinner("Booking interview..."):
                    payload = {"candidate_name": candidate_name, "candidate_email": candidate_email, "slot_time": selected_slot}
                    book_res = requests.post(f"{API_URL}/api/book-slot", json=payload)
                    if book_res.status_code == 200:
                        data = book_res.json().get("data", {})
                        st.success(f"✅ Interview Booked for {candidate_name}!")
                        st.markdown(f"**Google Meet:** [Join Here]({data.get('meet_link')})")
                    else:
                        st.error("Failed to book interview.")

# ==========================================
# TAB 3: POST-INTERVIEW FEEDBACK
# ==========================================
with tab3:
    st.header("Post-Interview Summary")
    fb_candidate = st.text_input("Candidate Name")
    fb_job = st.text_area("Job Description Reference", height=100)
    fb_notes = st.text_area("Notes", height=150)
    
    if st.button("🧠 Generate Recommendation"):
        if not fb_candidate or not fb_notes:
            st.warning("Provide name and notes.")
        else:
            with st.spinner("Analyzing..."):
                payload = {"candidate_name": fb_candidate, "job_description": fb_job, "interview_notes": fb_notes}
                fb_res = requests.post(f"{API_URL}/summarize-interview/", json=payload)
                if fb_res.status_code == 200:
                    data = fb_res.json().get("data", {})
                    rec = data.get('final_recommendation', 'Unknown')
                    color = "green" if "hire" in rec.lower() else "red"
                    st.markdown(f"### Recommendation: :{color}[{rec}]")
                    st.write(f"**Summary:** {data.get('interview_summary')}")
                    st.write(f"**Justification:** {data.get('justification')}")
                else:
                    st.error("Failed to generate summary.")