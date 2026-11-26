# AdaptLearn — AI-Based Adaptive Learning Framework

AdaptLearn is an intelligent adaptive learning platform built with **Python (Flask)**, **SQLite3**, **Tailwind CSS**, and **Chart.js**. It evaluates students through an initial diagnostic test, classifies their competency into dynamic tiers, and delivers personalized micro-learning materials.

---

## 🌟 Key Features

1. **Student Registration & Authentication**:
   - Secure student profile creation with hashed credentials (`pbkdf2:sha256`).
   - Session tracking and persistent learning history.

2. **Subject Selection (Python Track)**:
   - Structured 5-topic curriculum covering:
     1. Python Syntax & Variables
     2. Control Flow & Decision Making
     3. Loops & Iterations
     4. Functions & Scope
     5. Data Structures (Lists & Dictionaries)

3. **10-Question Diagnostic Assessment**:
   - 10 benchmark questions spanning fundamental to advanced Python concepts.
   - Real-time scoring and instant SQLite persistence.

4. **AI-Based Learning Level Classification**:
   - **Basic Tier (< 40%)**: Focuses on core syntax, intuitive mental models, and step-by-step guidance.
   - **Intermediate Tier (40% – 70%)**: Focuses on practical implementation, common edge-cases, and debugging.
   - **Advanced Tier (> 70%)**: Focuses on runtime internals, generators, closures, and algorithmic optimization.

5. **Adaptive Content Delivery**:
   - **Short Notes**: Concise markdown notes with syntax highlighting tailored to the student's tier.
   - **Short Clips**: Curated 4-7 minute instructional video clips embedded directly in the learning viewer.
   - **Key Takeaways**: Bite-sized summary cards for quick revision.

6. **Continuous Topic Micro-Assessments**:
   - Post-lesson 3-question assessments to verify knowledge.
   - Mastery threshold: $\ge 60\%$ advances to the next syllabus topic; $< 60\%$ triggers targeted remedial reinforcement.

7. **Performance Analytics & Reporting Dashboard**:
   - **Topic Mastery Radar Chart**: Visualizes competency coverage across all topics.
   - **Score Trajectory Line Chart**: Chronological score history.
   - **AI Diagnostic Synthesis**: Highlights specific strengths, targeted review areas, and next-action recommendations.

8. **Course Completion**:
   - Upon mastering all 5 topics, issues an official verified Certificate of Completion.

---

## 🚀 How to Run the Application

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database & Seed Curriculum
```bash
python database/seed_data.py
```

### 3. Launch the Server
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Running Automated Tests
```bash
python test_app.py
```
All unit tests, level classification boundary tests, quiz engines, and HTTP route integrations will be verified.

---

## 📁 Project Directory Structure
```text
mini-project/
├── app.py                      # Main Flask application & routes
├── config.py                   # Configuration & SQLite settings
├── requirements.txt            # Python dependencies
├── test_app.py                 # Automated unit & integration test suite
├── README.md                   # Documentation
│
├── database/
│   ├── schema.sql              # SQLite table definitions
│   ├── db.py                   # DB connection manager
│   └── seed_data.py            # Diagnostic questions, syllabus & materials
│
├── services/
│   ├── auth_service.py         # Registration & login
│   ├── ai_classifier.py        # <40%, 40-70%, >70% classification logic
│   ├── quiz_service.py         # 10-Q diagnostic & topic micro-quizzes
│   ├── adaptive_engine.py      # Tier-tailored content resolution
│   └── report_service.py       # Performance analytics & Chart.js data
│
├── static/
│   └── css/
│       └── custom.css          # Custom animations & aesthetic styling
│
└── templates/
    ├── base.html               # Shared layout & navigation
    ├── auth/
    │   ├── login.html          # Student login
    │   └── register.html       # Student registration
    ├── dashboard/
    │   ├── index.html          # Student learning hub
    │   └── reports.html        # Analytics & performance radar
    ├── quiz/
    │   ├── diagnostic.html     # 10-Question diagnostic test
    │   ├── diagnostic_result.html # AI level results & strengths/weaknesses
    │   └── topic_quiz.html     # Topic micro-assessment
    └── learning/
        ├── material_view.html  # Adaptive short notes & video player
        └── completion.html     # Course completion certificate
```
