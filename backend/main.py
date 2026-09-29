import io
import json
import random
import re
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

import pypdf
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ============================================================
# APP SETUP
# ============================================================

app = FastAPI(
    title="StudyFlow AI API",
    version="0.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_text_from_pdf(file_bytes: bytes) -> dict:
    """
    Extract text from every page of the uploaded PDF.
    """

    reader = pypdf.PdfReader(io.BytesIO(file_bytes))

    pages = []
    full_text = []

    for page_number, page in enumerate(reader.pages, start=1):

        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""

        text = text.strip()

        pages.append({
            "page": page_number,
            "text": text
        })

        full_text.append(
            f"--- Page {page_number} ---\n{text}"
        )

    combined = "\n\n".join(full_text)

    return {
        "total_pages": len(reader.pages),
        "pages": pages,
        "full_text": combined,
        "word_count": len(combined.split()),
    }


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text: str) -> str:
    """
    Clean extracted PDF text without changing its meaning.
    """

    if not text:
        return ""

    # Remove unusual control characters.
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", text)

    # Normalize spaces.
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ============================================================
# DOCUMENT PROFILE
# ============================================================

def build_document_profile(pages: list[dict]) -> str:
    """
    Create a compact representation of the CURRENT PDF.

    This is important for large PDFs because sending all 160+
    pages to a small local model is unnecessary and unreliable.

    We sample:
        - beginning
        - middle
        - end
        - pages containing likely headings
    """

    if not pages:
        return ""

    selected = []

    total = len(pages)

    # Beginning of document.
    beginning_count = min(12, total)

    for i in range(beginning_count):
        selected.append(pages[i])

    # Middle section.
    if total > 20:
        middle_start = max(0, total // 2 - 5)

        for i in range(middle_start, min(total, middle_start + 10)):
            selected.append(pages[i])

    # End of document.
    if total > 12:
        for page in pages[-10:]:
            selected.append(page)

    # Find pages with likely academic headings.
    heading_words = [
        "unit",
        "chapter",
        "module",
        "contents",
        "topic",
        "objectives",
        "process",
        "algorithm",
        "model",
        "architecture",
        "management",
        "introduction",
    ]

    for page in pages:
        lower = page["text"].lower()

        if any(word in lower for word in heading_words):
            selected.append(page)

        if len(selected) >= 55:
            break

    # Remove duplicate page numbers.
    unique = {}

    for page in selected:
        unique[page["page"]] = page

    selected = list(unique.values())

    selected.sort(key=lambda x: x["page"])

    result = []

    max_chars = 24000
    current_length = 0

    for page in selected:

        page_text = page["text"].strip()

        if not page_text:
            continue

        block = (
            f"\n--- PAGE {page['page']} ---\n"
            f"{page_text[:1400]}\n"
        )

        if current_length + len(block) > max_chars:
            break

        result.append(block)
        current_length += len(block)

    return "\n".join(result)


# ============================================================
# OLLAMA HELPER
# ============================================================

def call_ollama(
    prompt: str,
    timeout: int = 25,
    temperature: float = 0.1,
    num_predict: int = 700,
):
    """
    Call local Ollama.

    Returns the model response as text.
    Returns None if Ollama is unavailable.
    """

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
        },
    }

    try:

        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate",
            data=data,
            headers={
                "Content-Type": "application/json"
            },
            method="POST",
        )

        with urllib.request.urlopen(
            request,
            timeout=timeout
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        answer = result.get("response", "")

        if not answer:
            return None

        return answer.strip()

    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        OSError,
        json.JSONDecodeError,
    ) as error:

        print(
            f"[StudyFlow AI] Ollama unavailable: {error}"
        )

    except Exception as error:

        print(
            f"[StudyFlow AI] Ollama error: {error}"
        )

    return None


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json_object(text: str):
    """
    Safely extract a JSON object from an Ollama response.
    """

    if not text:
        return None

    text = text.strip()

    # Remove markdown code fences.
    text = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```\s*",
        "",
        text
    )

    # Try direct JSON first.
    try:
        return json.loads(text)
    except Exception:
        pass

    # Find JSON object.
    match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL
    )

    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except Exception:
        return None


def extract_json_array(text: str):
    """
    Safely extract a JSON array from an Ollama response.
    """

    if not text:
        return None

    text = text.strip()

    text = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```\s*",
        "",
        text
    )

    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(
        r"\[.*\]",
        text,
        re.DOTALL
    )

    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except Exception:
        return None


# ============================================================
# TOPIC NAME CLEANING
# ============================================================

GENERIC_TOPICS = {
    "",
    "introduction",
    "conclusion",
    "summary",
    "overview",
    "example",
    "examples",
    "simple example",
    "key takeaway",
    "quick revision",
    "revision",
    "important points",
    "contents",
    "objectives",
    "learning objectives",
    "references",
    "bibliography",
    "appendix",
    "chapter",
    "unit",
    "module",
    "topic",
    "study material",
    "course material",
}


def clean_topic_name(name: str) -> str:
    """
    Clean an AI-generated topic name.
    """

    name = str(name).strip()

    name = re.sub(
        r"^[\d\s.):-]+",
        "",
        name
    )

    name = re.sub(
        r"^(topic|chapter|unit|module|section)\s*[\d.:-]*\s*",
        "",
        name,
        flags=re.IGNORECASE
    )

    name = re.sub(
        r"\s+",
        " ",
        name
    )

    return name.strip(" -:;,.")


def is_valid_topic(name: str) -> bool:
    """
    Reject generic/noise topics.
    """

    if not name:
        return False

    lower = name.lower().strip()

    if lower in GENERIC_TOPICS:
        return False

    if len(name) < 3:
        return False

    if len(name) > 100:
        return False

    # Reject sentence-like topics.
    if len(name.split()) > 12:
        return False

    return True


# ============================================================
# GENERIC HEADING EXTRACTION
# ============================================================

def extract_candidate_headings(text: str) -> list[str]:
    """
    Extract likely academic headings directly from the CURRENT PDF.

    This is only a fallback if Ollama is unavailable.
    """

    candidates = []

    for raw_line in text.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        if len(line) > 100:
            continue

        words = line.split()

        if len(words) < 2 or len(words) > 10:
            continue

        # Remove page markers.
        if line.lower().startswith("--- page"):
            continue

        # Numbered heading:
        # 1. Process Management
        # 2.1 Process Scheduling
        numbered = re.match(
            r"^\d+(?:\.\d+)*[\s.)-]+(.+)$",
            line
        )

        if numbered:
            candidate = numbered.group(1).strip()

            if is_valid_topic(candidate):
                candidates.append(candidate)

            continue

        # Unit/chapter/section heading.
        labeled = re.match(
            r"^(unit|chapter|module|section|topic)\s*[\dA-Za-z.:-]*\s*(.+)$",
            line,
            flags=re.IGNORECASE
        )

        if labeled:
            candidate = labeled.group(2).strip()

            if is_valid_topic(candidate):
                candidates.append(candidate)

            continue

        # All caps headings.
        if line.isupper() and len(words) >= 2:

            if is_valid_topic(line):
                candidates.append(line.title())

            continue

        # Title case headings.
        title_like = 0

        for word in words:

            cleaned = re.sub(
                r"[^A-Za-z0-9]+",
                "",
                word
            )

            if not cleaned:
                continue

            if cleaned[0].isupper():
                title_like += 1

        if title_like >= max(2, len(words) // 2):

            if not line.endswith((".", ",", ";", ":")):

                if is_valid_topic(line):
                    candidates.append(line)

    # Remove duplicates.
    unique = []
    seen = set()

    for candidate in candidates:

        key = re.sub(
            r"\s+",
            " ",
            candidate.lower()
        ).strip()

        if key not in seen:

            seen.add(key)
            unique.append(candidate)

    return unique


# ============================================================
# SUBJECT + TOPIC DETECTION
# ============================================================

def detect_subject_and_topics(
    full_text: str,
    pages: list[dict],
    max_topics: int = 12,
) -> dict:
    """
    Detect the subject and topics from ONLY the CURRENT PDF.

    Important:
    There is NO hard-coded OOP-first detector here.

    The AI receives a profile built from the current PDF.
    """

    text = clean_text(full_text)

    if len(text) < 20:

        return {
            "subject": "Unknown",
            "topics": []
        }

    profile = build_document_profile(pages)

    if not profile:
        profile = text[:24000]

    prompt = f"""
You are StudyFlow AI, an academic document analyzer.

Analyze ONLY the study material supplied below.

The document may belong to ANY academic subject.

Examples of possible subjects include:
- Operating Systems
- Object-Oriented Programming
- Database Management Systems
- Computer Networks
- Data Structures
- Algorithms
- Computer Organization
- Software Engineering
- Mathematics
- Physics
- Electronics
- Electrical Engineering
- Artificial Intelligence
- Machine Learning
- Any other subject

Your job is to identify the actual subject represented by THIS document
and extract the most important study topics actually present in THIS document.

IMPORTANT RULES:

1. Use ONLY the supplied document.
2. Do NOT use information from previous requests.
3. Do NOT assume the document is OOP.
4. Do NOT assume the document is Operating Systems.
5. Do NOT invent topics.
6. Every topic must be supported by the supplied document.
7. Do not return generic headings such as:
   - Introduction
   - Summary
   - Conclusion
   - Example
   - References
   - Objectives
   - Overview
8. Do not return individual names such as Student, John, Alice, etc.
9. Combine closely related concepts when appropriate.
10. Use actual academic terminology from the document.
11. Return between 4 and {max_topics} meaningful topics when possible.
12. The subject should describe the actual academic subject of the document,
    not simply "Computer Science" unless the document truly is general.
13. If the document is clearly a UNIT from a larger subject, identify the
    larger subject when the document provides enough evidence.
14. Do not create a topic just because a word appears once.
15. Focus on concepts that are repeatedly discussed or clearly presented
    as sections/topics.

Return ONLY valid JSON in exactly this format:

{{
  "subject": "Operating Systems",
  "topics": [
    {{
      "name": "Process Management",
      "importance": "high"
    }},
    {{
      "name": "Process Scheduling",
      "importance": "high"
    }}
  ]
}}

CURRENT DOCUMENT:

{profile}
"""

    response = call_ollama(
        prompt,
        timeout=35,
        temperature=0.05,
        num_predict=800
    )

    if response:

        parsed = extract_json_object(response)

        if isinstance(parsed, dict):

            subject = str(
                parsed.get("subject", "Unknown")
            ).strip()

            raw_topics = parsed.get(
                "topics",
                []
            )

            topics = []

            if isinstance(raw_topics, list):

                for index, item in enumerate(raw_topics):

                    if isinstance(item, dict):

                        name = clean_topic_name(
                            item.get("name", "")
                        )

                        importance = str(
                            item.get(
                                "importance",
                                "medium"
                            )
                        ).lower()

                    else:

                        name = clean_topic_name(item)
                        importance = "medium"

                    if not is_valid_topic(name):
                        continue

                    if importance not in {
                        "high",
                        "medium",
                        "low"
                    }:
                        importance = "medium"

                    if importance == "high":
                        base_score = 10
                    elif importance == "medium":
                        base_score = 7
                    else:
                        base_score = 4

                    score = max(
                        1,
                        base_score - index
                    )

                    topics.append({
                        "topic": name,
                        "score": score,
                        "importance": importance,
                        "keywords_found": name.split()[:5],
                    })

            # Remove duplicate AI topics.
            unique_topics = []
            seen = set()

            for topic in topics:

                key = topic["topic"].lower()

                if key in seen:
                    continue

                seen.add(key)
                unique_topics.append(topic)

            if unique_topics:

                return {
                    "subject": subject or "Academic Subject",
                    "topics": unique_topics[:max_topics]
                }

    # ========================================================
    # FALLBACK
    # ========================================================

    # If Ollama is unavailable, use headings FROM THIS PDF.
    headings = extract_candidate_headings(text)

    fallback_topics = []

    for index, heading in enumerate(headings[:max_topics]):

        fallback_topics.append({
            "topic": heading,
            "score": max(
                1,
                10 - index
            ),
            "importance": (
                "high"
                if index < 4
                else "medium"
            ),
            "keywords_found": heading.split()[:5],
        })

    # Try to infer a basic subject from the document's own title/content.
    subject = infer_subject_from_document(text)

    return {
        "subject": subject,
        "topics": fallback_topics
    }


# ============================================================
# LOCAL SUBJECT FALLBACK
# ============================================================

def infer_subject_from_document(text: str) -> str:
    """
    Basic fallback subject detection.

    This is NOT used when Ollama successfully identifies
    the subject.

    It only uses words actually present in the CURRENT PDF.
    """

    lower = text.lower()

    subject_patterns = [
        (
            "Operating Systems",
            [
                "operating systems",
                "operating system",
                "process scheduling",
                "process management",
                "interprocess communication",
                "deadlock",
            ]
        ),
        (
            "Object-Oriented Programming",
            [
                "object-oriented programming",
                "object oriented programming",
                "inheritance",
                "polymorphism",
                "encapsulation",
                "constructors",
            ]
        ),
        (
            "Database Management Systems",
            [
                "database management system",
                "dbms",
                "relational database",
                "normalization",
                "sql",
            ]
        ),
        (
            "Computer Networks",
            [
                "computer networks",
                "computer network",
                "osi model",
                "tcp/ip",
                "routing",
                "network layer",
            ]
        ),
        (
            "Data Structures",
            [
                "data structures",
                "linked list",
                "stack",
                "queue",
                "binary tree",
                "graph traversal",
            ]
        ),
        (
            "Machine Learning",
            [
                "machine learning",
                "supervised learning",
                "unsupervised learning",
                "regression",
                "classification",
                "neural network",
            ]
        ),
    ]

    best_subject = "Academic Subject"
    best_score = 0

    for subject, keywords in subject_patterns:

        score = 0

        for keyword in keywords:

            if keyword in lower:
                score += 1

        if score > best_score:

            best_score = score
            best_subject = subject

    return best_subject


# ============================================================
# MAIN TOPIC EXTRACTION
# ============================================================

def extract_topics(
    text: str,
    pages: list[dict],
    max_topics: int = 12,
) -> dict:
    """
    Main topic extraction.

    IMPORTANT:
    Every call receives the current PDF's text/pages.
    Nothing from previous uploads is stored.
    """

    return detect_subject_and_topics(
        text,
        pages,
        max_topics
    )


# ============================================================
# REQUEST MODELS
# ============================================================

class StudyPlanRequest(BaseModel):
    topics: list[str]
    exam_date: str
    daily_hours: float


class QuizRequest(BaseModel):
    text: str
    num_questions: int = 5


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "version": "0.2.0",
        "ollama_model": OLLAMA_MODEL,
    }


# ============================================================
# PDF UPLOAD
# ============================================================

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...)
):
    """
    Upload a PDF, extract its text and detect its subject/topics.

    Every upload is processed independently.
    """

    if (
        not file.filename
        or not file.filename.lower().endswith(".pdf")
    ):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted."
        )

    content = await file.read()

    if not content:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    try:

        extracted = extract_text_from_pdf(
            content
        )

    except Exception as error:

        raise HTTPException(
            status_code=422,
            detail=f"Could not parse PDF: {error}"
        )

    if not extracted["full_text"].strip():

        raise HTTPException(
            status_code=422,
            detail=(
                "No readable text was found in this PDF. "
                "Please upload a text-based PDF."
            )
        )

    detected = extract_topics(
        extracted["full_text"],
        extracted["pages"]
    )

    return {
        "filename": file.filename,
        "total_pages": extracted["total_pages"],
        "word_count": extracted["word_count"],
        "pages": extracted["pages"],
        "full_text": extracted["full_text"],
        "subject": detected["subject"],
        "detected_topics": detected["topics"],
    }


# ============================================================
# STUDY PLAN
# ============================================================

@app.post("/study-plan")
def generate_study_plan(
    req: StudyPlanRequest
):
    """
    Generate a day-by-day study plan.
    """

    try:

        exam = date.fromisoformat(
            req.exam_date
        )

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail="Invalid exam_date format. Use YYYY-MM-DD."
        )

    today = date.today()

    days_left = (
        exam - today
    ).days

    if days_left <= 0:

        raise HTTPException(
            status_code=400,
            detail="Exam date must be in the future."
        )

    if req.daily_hours <= 0:

        raise HTTPException(
            status_code=400,
            detail="daily_hours must be greater than 0."
        )

    topics = [
        str(topic).strip()
        for topic in req.topics
        if str(topic).strip()
    ]

    if not topics:
        topics = [
            "General Review"
        ]

    daily_hours = round(
        req.daily_hours,
        1
    )

    total_study_hours = round(
        days_left * daily_hours,
        1
    )

    # Reserve final days for revision.
    if days_left >= 6:
        final_review_days = 2
    elif days_left >= 3:
        final_review_days = 1
    else:
        final_review_days = 0

    learning_days = max(
        1,
        days_left - final_review_days
    )

    # Distribute topics.
    topic_slots = []

    for index in range(learning_days):

        topic_slots.append(
            topics[
                index % len(topics)
            ]
        )

    plan_days = []

    current_day = (
        today + timedelta(days=1)
    )

    for day_num in range(
        1,
        days_left + 1
    ):

        if day_num <= learning_days:

            topic = topic_slots[
                day_num - 1
            ]

            cycle = (
                day_num - 1
            ) % 3

            if cycle == 0:

                tasks = [
                    f"Learn {topic}: read the notes and understand the key concepts.",
                    f"Write short notes for {topic}.",
                ]

            elif cycle == 1:

                tasks = [
                    f"Practice {topic}: solve questions and examples.",
                    f"Review difficult parts of {topic}.",
                ]

            else:

                tasks = [
                    f"Revise {topic}: recall the important concepts without notes.",
                    f"Test yourself on {topic}.",
                ]

            plan_topics = [
                topic
            ]

        else:

            tasks = [
                "Revise all detected topics.",
                "Review difficult concepts and important definitions.",
                "Practice questions from the complete syllabus.",
                "Test yourself and review mistakes.",
            ]

            plan_topics = topics

        plan_days.append({
            "day": day_num,
            "date": current_day.isoformat(),
            "topics": plan_topics,
            "hours": daily_hours,
            "tasks": tasks,
        })

        current_day += timedelta(
            days=1
        )

    return {
        "days_left": days_left,
        "total_study_hours": total_study_hours,
        "hours_per_topic": round(
            total_study_hours / len(topics),
            1
        ),
        "topics": topics,
        "learning_days": learning_days,
        "revision_days": final_review_days,
        "plan": plan_days,
    }


# ============================================================
# QUIZ GENERATION
# ============================================================

@app.post("/quiz")
def generate_quiz(
    req: QuizRequest
):
    """
    Generate conceptual MCQs from the CURRENT uploaded PDF text.
    """

    text = req.text.strip()

    if not text:

        raise HTTPException(
            status_code=400,
            detail="Text is required to generate a quiz."
        )

    num_questions = max(
        3,
        min(req.num_questions, 15)
    )

    # Use representative text for very large PDFs.
    source_text = build_quiz_source(
        text
    )

    prompt = f"""
You are an expert college-level examination question setter.

Create exactly {num_questions} multiple-choice questions using ONLY
the study material below.

IMPORTANT:

1. Use only information found in the supplied material.
2. Do not use outside knowledge.
3. Do not assume the subject.
4. Questions must be related to the actual document.
5. Prefer conceptual, application and comparison questions.
6. Avoid simple one-word definition questions when possible.
7. Do not create fill-in-the-blank questions.
8. Do not use "_____".
9. Each question must have exactly 4 options.
10. There must be exactly one correct answer.
11. Distractors should be plausible and related to the same subject.
12. Do not repeat questions.

Return ONLY valid JSON:

{{
  "questions": [
    {{
      "question": "Question text",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "answer": "Option A"
    }}
  ]
}}

STUDY MATERIAL:

{source_text}
"""

    response = call_ollama(
        prompt,
        timeout=12,
        temperature=0.45,
        num_predict=1400
    )

    if response:

        parsed = extract_json_object(
            response
        )

        if isinstance(parsed, dict):

            raw_questions = parsed.get(
                "questions",
                []
            )

            valid_questions = []
            seen = set()

            if isinstance(
                raw_questions,
                list
            ):

                for item in raw_questions:

                    if not isinstance(
                        item,
                        dict
                    ):
                        continue

                    question = str(
                        item.get(
                            "question",
                            ""
                        )
                    ).strip()

                    options = item.get(
                        "options",
                        []
                    )

                    answer = str(
                        item.get(
                            "answer",
                            ""
                        )
                    ).strip()

                    if not question:
                        continue

                    if not isinstance(
                        options,
                        list
                    ):
                        continue

                    options = [
                        str(option).strip()
                        for option in options
                        if str(option).strip()
                    ]

                    # Remove duplicate options.
                    options = list(
                        dict.fromkeys(
                            options
                        )
                    )

                    lower_question = (
                        question.lower()
                    )

                    if (
                        "fill in the blank"
                        in lower_question
                        or "_____" in question
                        or "______" in question
                    ):
                        continue

                    if len(options) != 4:
                        continue

                    if answer not in options:
                        continue

                    key = re.sub(
                        r"\s+",
                        " ",
                        lower_question
                    )

                    if key in seen:
                        continue

                    seen.add(key)

                    valid_questions.append({
                        "id": len(valid_questions) + 1,
                        "question": question,
                        "options": options,
                        "answer": answer,
                    })

                    if len(valid_questions) >= num_questions:
                        break

            if len(valid_questions) >= min(
                3,
                num_questions
            ):

                return {
                    "questions": valid_questions,
                    "total": len(valid_questions),
                    "source": "ollama",
                }

    # ========================================================
    # LOCAL FALLBACK
    # ========================================================

    fallback = generate_fallback_quiz(
        text,
        num_questions
    )

    if fallback:

        return {
            "questions": fallback,
            "total": len(fallback),
            "source": "document-fallback",
        }

    raise HTTPException(
        status_code=422,
        detail=(
            "Could not generate enough questions "
            "from the provided study material."
        )
    )


# ============================================================
# QUIZ SOURCE BUILDER
# ============================================================

def build_quiz_source(
    text: str
) -> str:
    """
    Keep quiz generation manageable for large PDFs.

    Uses:
        beginning
        middle
        end
    """

    if len(text) <= 16000:
        return text

    length = len(text)

    beginning = text[:6000]

    middle_start = (
        length // 2
    ) - 3000

    middle = text[
        max(0, middle_start):
        max(0, middle_start) + 6000
    ]

    ending = text[-4000:]

    return (
        beginning
        + "\n\n--- MIDDLE OF DOCUMENT ---\n\n"
        + middle
        + "\n\n--- END OF DOCUMENT ---\n\n"
        + ending
    )


# ============================================================
# FALLBACK QUIZ
# ============================================================

def generate_fallback_quiz(
    text: str,
    num_questions: int
) -> list[dict]:
    """
    Generate basic conceptual questions from the CURRENT PDF.

    This fallback is intentionally subject-neutral.
    """

    lower = text.lower()

    question_bank = []

    # --------------------------------------------------------
    # Operating Systems
    # --------------------------------------------------------

    if (
        "operating system" in lower
        or "process scheduling" in lower
        or "interprocess communication" in lower
    ):

        if (
            "process scheduling" in lower
            and "context switch" in lower
        ):

            question_bank.append({
                "question": (
                    "Which activity is most directly associated "
                    "with changing the CPU from one process to another?"
                ),
                "options": [
                    "Context switching",
                    "File allocation",
                    "Memory compaction",
                    "Disk formatting",
                ],
                "answer": "Context switching",
            })

        if (
            "interprocess communication" in lower
            and "shared memory" in lower
        ):

            question_bank.append({
                "question": (
                    "Which IPC approach allows processes to communicate "
                    "by accessing a common region of memory?"
                ),
                "options": [
                    "Shared memory",
                    "Remote procedure call",
                    "Context switching",
                    "CPU scheduling",
                ],
                "answer": "Shared memory",
            })

        if (
            "message passing" in lower
            and "process" in lower
        ):

            question_bank.append({
                "question": (
                    "Which IPC mechanism communicates by sending and "
                    "receiving messages between processes?"
                ),
                "options": [
                    "Message passing",
                    "Memory paging",
                    "Process termination",
                    "Context switching",
                ],
                "answer": "Message passing",
            })

        if (
            "process control block" in lower
        ):

            question_bank.append({
                "question": (
                    "Which operating-system structure stores information "
                    "associated with a process?"
                ),
                "options": [
                    "Process Control Block",
                    "Page Table",
                    "File Allocation Table",
                    "Instruction Register",
                ],
                "answer": "Process Control Block",
            })

        if (
            "critical section" in lower
        ):

            question_bank.append({
                "question": (
                    "What problem is a critical-section solution primarily "
                    "designed to address?"
                ),
                "options": [
                    "Concurrent access to shared data",
                    "Disk formatting",
                    "File compression",
                    "Instruction decoding",
                ],
                "answer": "Concurrent access to shared data",
            })

    # --------------------------------------------------------
    # OOP
    # --------------------------------------------------------

    if (
        "object-oriented programming" in lower
        or "object oriented programming" in lower
        or "inheritance" in lower
        or "polymorphism" in lower
    ):

        if "inheritance" in lower:

            question_bank.append({
                "question": (
                    "A child class receives properties and methods from "
                    "another class. Which OOP concept does this represent?"
                ),
                "options": [
                    "Inheritance",
                    "Encapsulation",
                    "Abstraction",
                    "Method overloading",
                ],
                "answer": "Inheritance",
            })

        if "polymorphism" in lower:

            question_bank.append({
                "question": (
                    "Which OOP concept allows the same interface or operation "
                    "to have different implementations?"
                ),
                "options": [
                    "Polymorphism",
                    "Encapsulation",
                    "Constructor",
                    "Inheritance",
                ],
                "answer": "Polymorphism",
            })

        if "encapsulation" in lower:

            question_bank.append({
                "question": (
                    "A class hides its internal data and provides controlled "
                    "methods for accessing it. Which concept is illustrated?"
                ),
                "options": [
                    "Encapsulation",
                    "Inheritance",
                    "Polymorphism",
                    "Overloading",
                ],
                "answer": "Encapsulation",
            })

        if "abstraction" in lower:

            question_bank.append({
                "question": (
                    "Which concept focuses on exposing essential behavior "
                    "while hiding implementation details?"
                ),
                "options": [
                    "Abstraction",
                    "Inheritance",
                    "Overloading",
                    "Instantiation",
                ],
                "answer": "Abstraction",
            })

    # --------------------------------------------------------
    # Computer Networks
    # --------------------------------------------------------

    if (
        "osi model" in lower
        or "tcp/ip" in lower
        or "computer network" in lower
    ):

        if "osi model" in lower:

            question_bank.append({
                "question": (
                    "Which model organizes network communication into "
                    "separate conceptual layers?"
                ),
                "options": [
                    "OSI model",
                    "Relational model",
                    "Process model",
                    "Object model",
                ],
                "answer": "OSI model",
            })

        if "tcp/ip" in lower:

            question_bank.append({
                "question": (
                    "Which protocol suite is commonly associated with "
                    "Internet communication?"
                ),
                "options": [
                    "TCP/IP",
                    "OOP",
                    "SQL",
                    "POSIX",
                ],
                "answer": "TCP/IP",
            })

    # --------------------------------------------------------
    # DBMS
    # --------------------------------------------------------

    if (
        "database management system" in lower
        or "dbms" in lower
        or "normalization" in lower
    ):

        if "normalization" in lower:

            question_bank.append({
                "question": (
                    "What is the main purpose of normalization in a "
                    "relational database?"
                ),
                "options": [
                    "Reduce data redundancy",
                    "Increase duplicate data",
                    "Remove all tables",
                    "Disable relationships",
                ],
                "answer": "Reduce data redundancy",
            })

        if "sql" in lower:

            question_bank.append({
                "question": (
                    "Which language is primarily used to query and manage "
                    "data in relational database systems?"
                ),
                "options": [
                    "SQL",
                    "HTML",
                    "CSS",
                    "HTTP",
                ],
                "answer": "SQL",
            })

    # --------------------------------------------------------
    # Data Structures
    # --------------------------------------------------------

    if (
        "data structures" in lower
        or "linked list" in lower
        or "stack" in lower
        or "queue" in lower
    ):

        if "stack" in lower:

            question_bank.append({
                "question": (
                    "Which access principle is normally associated "
                    "with a stack?"
                ),
                "options": [
                    "LIFO",
                    "FIFO",
                    "Random-only access",
                    "Priority-only access",
                ],
                "answer": "LIFO",
            })

        if "queue" in lower:

            question_bank.append({
                "question": (
                    "Which access principle is normally associated "
                    "with a queue?"
                ),
                "options": [
                    "FIFO",
                    "LIFO",
                    "Random-only access",
                    "Reverse-priority access",
                ],
                "answer": "FIFO",
            })

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    unique = []
    seen = set()

    for item in question_bank:

        key = re.sub(
            r"\s+",
            " ",
            item["question"].lower()
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(item)

    random.shuffle(unique)

    selected = unique[:num_questions]

    questions = []

    for item in selected:

        options = item["options"][:]

        random.shuffle(options)

        questions.append({
            "id": len(questions) + 1,
            "question": item["question"],
            "options": options,
            "answer": item["answer"],
        })

    return questions


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )