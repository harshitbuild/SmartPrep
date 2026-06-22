import streamlit as st
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from google import genai
from google.genai import errors
import database as db
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
db.init_db()
st.set_page_config(page_title="SmartPrep Study Portal", page_icon="🎓", layout="wide")
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if not st.session_state.logged_in:
    st.title("📚 SmartPrep Study Portal - System Login")
    
    auth_mode = st.radio("Choose Action:", ["Login", "Register/Sign Up"])
    
    username = st.text_input("Username / Email")
    password = st.text_input("Password", type="password")
    
    if auth_mode == "Login":
        if st.button("Login"):
            if db.check_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Invalid Username or Password.")
                
    elif auth_mode == "Register/Sign Up":
        if st.button("Register"):
            if username and password:
                if db.add_user(username, password):
                    st.success("Account created successfully! Please switch to 'Login' mode.")
                else:
                    st.error("Username already taken. Try another one.")
            else:
                st.warning("Please fill all fields.")
else:
    st.sidebar.title(f"👤 Account: {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
    tab1, tab2 = st.tabs(["💬 AI Professor Workspace", "🎯 Unique Feature: AI Technical Mock Interviewer"])
    st.sidebar.title("📁 Upload Core Study Material")
    uploaded_file = st.sidebar.file_uploader("Upload notes or textbook (PDF)", type=["pdf"])

    pdf_text = ""
    if uploaded_file is not None:
        st.sidebar.success("PDF Context Loaded!")
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pdf_text += text + "\n"
    with tab1:
        st.title("📚 SmartPrep Study Assistant & Doubt Solver")
        st.write("Ask queries, demand clear definitions, or ask your professor to write optimized code templates.")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if user_question := st.chat_input("Ask a doubt..."):
            with st.chat_message("user"):
                st.markdown(user_question)
            st.session_state.messages.append({"role": "user", "content": user_question})

            system_instruction = (
                "You are an encouraging and highly knowledgeable Professor. Your goal is to break down complex academic "
                "topics into very simple, easy-to-understand bullet points with real-world examples."
            )
            
            full_prompt = f"{system_instruction}\n\nContext from uploaded PDF:\n{pdf_text[:10000]}\n\nStudent Question: {user_question}" if pdf_text else f"{system_instruction}\n\nStudent Question: {user_question}"

            try:
                if not api_key: raise Exception("API Key not found.")
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(model='gemini-2.5-flash', contents=full_prompt)
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")
    with tab2:
        st.title("🎯 Real-Time AI Viva & Mock Interview Simulator")
        st.write("This feature evaluates your conceptual strength based on your notes or general computer science topics.")
        if "interview_started" not in st.session_state: st.session_state.interview_started = False
        if "current_question" not in st.session_state: st.session_state.current_question = ""
        if "question_count" not in st.session_state: st.session_state.question_count = 0
        if "interview_log" not in st.session_state: st.session_state.interview_log = []

        if not st.session_state.interview_started:
            st.info("💡 Click the button below to trigger an automated 3-Question Technical Interview based on your context.")
            if st.button("🚀 Start Mock Interview Session"):
                st.session_state.interview_started = True
                st.session_state.question_count = 1
                st.session_state.interview_log = []
                base_prompt = f"Based on this context: {pdf_text[:5000]}" if pdf_text else "Based on core B.Tech Computer Science core fundamentals."
                gen_prompt = f"{base_prompt} Generate exactly 1 highly technical, conceptual short question for a student interview. Do not provide answers, context, or extra text. Just the question string."
                
                try:
                    client = genai.Client(api_key=api_key)
                    resp = client.models.generate_content(model='gemini-2.5-flash', contents=gen_prompt)
                    st.session_state.current_question = resp.text
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to generate session: {e}")
        else:
            if st.session_state.question_count <= 3:
                st.subheader(f"❓ Question {st.session_state.question_count} of 3")
                st.info(st.session_state.current_question)
                
                student_ans = st.text_area("Type your detailed technical answer here:", key=f"ans_{st.session_state.question_count}")
                
                if st.button("Submit Answer & Next"):
                    if student_ans.strip() == "":
                        st.warning("Please type an answer before proceeding.")
                    else:
                        st.session_state.interview_log.append({
                            "question": st.session_state.current_question,
                            "answer": student_ans
                        })
                        
                        if st.session_state.question_count < 3:
                            st.session_state.question_count += 1
                            history_context = str(st.session_state.interview_log)
                            gen_prompt = f"Generate the next unique technical interview question. Avoid repeating these questions: {history_context}. Context: {pdf_text[:5000] if pdf_text else 'CS Core Basics'}. Return only the question text."
                            try:
                                client = genai.Client(api_key=api_key)
                                resp = client.models.generate_content(model='gemini-2.5-flash', contents=gen_prompt)
                                st.session_state.current_question = resp.text
                                st.rerun()
                            except Exception as e:
                                st.error(f"Network error: {e}")
                        else:
                            st.session_state.question_count += 1
                            st.rerun()
            else:
                st.success("🎉 Interview Session Completed Successfully!")
                st.subheader("📊 AI Performance Scorecard & Detailed Analytics")
                eval_prompt = f"Analyze this interview transcript for a B.Tech student:\n{str(st.session_state.interview_log)}\n\nProvide a performance evaluation report with:\n1. Strengths\n2. Weaknesses\n3. Estimated Core Score out of 100\n4. A neat markdown table representing mock score bars."
                
                with st.spinner("AI Professor is evaluating your transcript..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        eval_resp = client.models.generate_content(model='gemini-2.5-flash', contents=eval_prompt)
                        st.markdown(eval_resp.text)
                    except Exception as e:
                        st.error(f"Evaluation error: {e}")
                        
                if st.button("🔄 Reset & Take Another Interview"):
                    st.session_state.interview_started = False
                    st.rerun()