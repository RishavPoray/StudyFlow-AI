# 📚 StudyFlow AI

> **An AI-powered study assistant that turns your study material into a personalized learning workflow.**

StudyFlow AI analyzes uploaded academic PDFs, identifies the important topics, creates a personalized study plan, and generates conceptual quizzes to help students prepare more effectively.

## ✨ Features

* 📄 **PDF Upload & Text Extraction**

  * Upload academic PDF study material.
  * Extracts text and page information automatically.

* 🧠 **AI Topic Detection**

  * Identifies the subject and important topics from the uploaded document.
  * Works across different academic subjects.

* 📅 **Personalized Study Plan**

  * Generates a study schedule based on topics, available study time, and exam date.
  * Organizes learning, practice, and revision.

* 📝 **AI Quiz Generation**

  * Creates conceptual multiple-choice questions.
  * Provides four answer options and evaluates the user's answers.

* 🎯 **Quiz Results**

  * Shows score and performance after completing the quiz.

* 💻 **Local AI**

  * Uses Ollama with `llama3.2:3b`.
  * No paid AI API is required.

## 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │      Student        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React Frontend    │
                    │      Vite UI        │
                    └──────────┬──────────┘
                               │ HTTP
                               ▼
                    ┌─────────────────────┐
                    │   FastAPI Backend   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
       ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
       │ PDF Text    │  │    Topic    │  │ Study Plan  │
       │ Extraction  │  │  Detection  │  │ & Quiz      │
       └─────────────┘  └──────┬──────┘  └──────┬──────┘
                                │                │
                                └───────┬────────┘
                                        ▼
                              ┌──────────────────┐
                              │ Ollama           │
                              │ llama3.2:3b      │
                              └──────────────────┘
```

## 🛠️ Tech Stack

### Frontend

* React
* Vite
* JavaScript
* CSS

### Backend

* Python
* FastAPI
* Uvicorn
* pypdf

### AI

* Ollama
* Llama 3.2 3B

## 📁 Project Structure

```text
StudyFlow-AI/
│
├── backend/
│   ├── main.py
│   ├── ai_service.py
│   ├── pdf_service.py
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── components/
│   ├── package.json
│   └── vite.config.js
│
├── sample_docs/
│
├── .gitignore
└── README.md
```

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/RishavPoray/StudyFlow-AI.git
cd StudyFlow-AI
```

### 2. Set up Ollama

Install Ollama from:

https://ollama.com/

Then download the required model:

```bash
ollama pull llama3.2:3b
```

Make sure Ollama is running before starting the backend.

### 3. Set up the backend

Open a terminal:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn main:app --reload
```

Backend will run at:

```text
http://127.0.0.1:8000
```

### 4. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## 🔄 How It Works

```text
1. Student uploads a PDF
           ↓
2. StudyFlow extracts the PDF text
           ↓
3. AI analyzes the current document
           ↓
4. Important topics are identified
           ↓
5. Student provides exam/study preferences
           ↓
6. Personalized study plan is generated
           ↓
7. AI generates a conceptual quiz
           ↓
8. Student completes the quiz
           ↓
9. Results are displayed
```

## 🎯 Problem

Students often have large amounts of study material but struggle to decide:

* What topics should I study first?
* How should I divide my time?
* Have I understood the important concepts?
* How can I practice after studying?

StudyFlow AI brings these steps into one workflow.

## 💡 Solution

StudyFlow AI converts existing study material into an actionable learning workflow.

Instead of manually reading through a large document and creating a study schedule and questions, students can upload their material and let the application organize the learning process.

## 🔐 Privacy & Cost

StudyFlow AI is designed around local processing.

The AI model runs through Ollama on the user's machine, so no paid cloud AI API is required for the core AI functionality.

## 🚀 Future Improvements

Possible future additions include:

* Flashcard generation
* Progress tracking
* More document formats
* Automatic revision reminders
* Learning analytics
* More advanced question types
* Cloud deployment

## 👨‍💻 Author

**Rishav Poray**

GitHub:
https://github.com/RishavPoray

## 📄 License

This project is currently intended as a hackathon/educational project.
