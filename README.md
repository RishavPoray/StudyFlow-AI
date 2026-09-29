# StudyFlow AI

A local-only study assistant prototype. Upload a PDF, extract text, detect topics, generate a study plan, take a quiz, and see your weak areas.

## Stack
- **Frontend**: React + Vite (port 5173)
- **Backend**: FastAPI + Python (port 8000)
- **PDF extraction**: pypdf

---

## Quick Start

### 1 — Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2 — Frontend (new terminal)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## Features (Phase 1)
- [x] PDF upload (drag-and-drop or click)
- [x] Text extraction page-by-page (pypdf)
- [x] Detected topic display (keyword scoring)
- [x] Study plan generation (days × hours distribution)
- [x] Multiple-choice quiz from extracted text
- [x] Score + weak topic breakdown

## Project Structure

```
studyflow-ai/
├── backend/
│   ├── main.py            ← FastAPI app
│   ├── requirements.txt
│   └── uploads/           ← (unused, reserved for future file persistence)
└── frontend/
    ├── src/
    │   ├── App.jsx        ← all UI components
    │   └── index.css      ← design system
    ├── index.html
    ├── package.json
    └── vite.config.js     ← proxies /api → localhost:8000
```
