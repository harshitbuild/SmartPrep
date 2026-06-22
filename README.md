A full-stack, B.Tech-level smart learning ecosystem built with Python, Streamlit, and the latest Google GenAI SDK (gemini-2.5-flash). It offers secure user authentication, dynamic PDF-based knowledge contextualization, and a unique automated mock interview simulator.

1. **Secure Authentication System**: User login and registration framework powered by an integrated SQLite database with SHA-256 password hashing.
2. **AI Professor Workspace**: Contextual doubt-solving engine that extracts text from uploaded PDF materials to provide crisp, academic-focused explanations with real-world analogies.
3. **Automated Technical Mock Interviewer**: An interactive, stateful 3-question viva loop that dynamically adapts based on student inputs, analyzes performance transcripts, and yields an AI-generated evaluation report.

* **app.py**: Main Streamlit UI dashboard and state management loop.
* **database.py**: Database operations (SQLite table initialization, cryptographic hash checks, user creation).
* **requirements.txt**: Log of application dependencies.
* **.env**: Environment configuration storing the secure GEMINI_API_KEY.

### Setup Instructions

1. Activate your virtual environment.
2. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your key:
```env
   GEMINI_API_KEY=your_api_key_here
```
