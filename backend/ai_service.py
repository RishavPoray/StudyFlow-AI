"""
Modular AI Service for StudyFlow AI.

Supports local Ollama if available, with intelligent offline
heuristic fallbacks.

Main features:
1. AI topic extraction
2. Study plan generation
3. Quiz generation
4. Quiz analysis
"""

import json
import re
import random
import urllib.request
import urllib.error
from datetime import datetime, date
from typing import List, Dict, Any, Optional


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

OLLAMA_BASE_URL = "http://localhost:11434"

_cached_model = None
_ollama_checked = False


def check_ollama() -> Optional[str]:
    """
    Checks if Ollama is accessible and returns the first
    available model name.
    """

    global _cached_model, _ollama_checked

    try:
        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/tags",
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=2.0) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                models = data.get("models", [])

                if models:
                    # Prefer the model you installed for StudyFlow AI
                    preferred_models = [
                        "llama3.2:3b",
                        "llama3.2",
                        "llama3",
                        "mistral",
                        "phi3",
                        "gemma",
                        "llama2"
                    ]

                    available = [
                        model.get("name", "")
                        for model in models
                    ]

                    for preferred in preferred_models:
                        for available_model in available:
                            if (
                                available_model == preferred
                                or available_model.startswith(preferred + ":")
                            ):
                                _cached_model = available_model
                                _ollama_checked = True
                                return _cached_model

                    # Otherwise use the first installed model
                    _cached_model = models[0].get(
                        "name",
                        "llama3.2:3b"
                    )

                    _ollama_checked = True
                    return _cached_model

    except Exception:
        pass

    _cached_model = None
    _ollama_checked = True

    return None


def query_ollama(
    prompt: str,
    system: str = "",
    timeout: float = 30.0
) -> Optional[str]:
    """
    Calls local Ollama generate API.

    Returns:
        Response string or None if Ollama is unavailable.
    """

    model = check_ollama()

    if not model:
        return None

    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "keep_alive": "15m",
            "options": {
                "temperature": 0.1,
                "num_predict": 500
            }
        }

        data_bytes = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            f"{OLLAMA_BASE_URL}/api/generate",
            data=data_bytes,
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=timeout) as resp:

            if resp.status == 200:
                result = json.loads(
                    resp.read().decode("utf-8")
                )

                return result.get("response", "").strip()

    except Exception as e:
        print(
            f"[AI Service] Ollama call failed: {e}. "
            f"Using fallback engine."
        )

    return None


# ============================================================
# 1. TOPIC EXTRACTION
# ============================================================

KNOWN_TOPIC_SETS = [
    {
        "keywords": [
            "osi",
            "tcp/ip",
            "packet",
            "layer",
            "router",
            "switch",
            "topology",
            "protocol"
        ],
        "topics": [
            "OSI Model",
            "TCP/IP Suite",
            "Network Devices",
            "Network Topologies",
            "Protocols and Ports"
        ]
    },

    {
        "keywords": [
            "database",
            "sql",
            "relational",
            "normalization",
            "acid",
            "transaction",
            "index"
        ],
        "topics": [
            "Database Architecture",
            "SQL Queries",
            "Relational Normalization",
            "ACID Transactions",
            "Indexing and Optimization"
        ]
    },

    {
        "keywords": [
            "operating system",
            "process",
            "thread",
            "deadlock",
            "memory management",
            "scheduling",
            "paging"
        ],
        "topics": [
            "Processes and Threads",
            "CPU Scheduling",
            "Deadlock Handling",
            "Memory Management and Paging",
            "File Systems"
        ]
    },

    {
        "keywords": [
            "machine learning",
            "neural",
            "supervised",
            "regression",
            "classification",
            "gradient",
            "overfitting"
        ],
        "topics": [
            "Supervised Learning",
            "Regression and Classification",
            "Neural Networks",
            "Overfitting and Regularization",
            "Model Evaluation"
        ]
    }
]


GENERIC_TOPIC_WORDS = {
    "student",
    "students",
    "class",
    "classes",
    "object",
    "objects",
    "method",
    "methods",
    "programming",
    "program",
    "example",
    "examples",
    "simple example",
    "introduction",
    "overview",
    "summary",
    "conclusion",
    "key takeaway",
    "takeaway",
    "chapter",
    "section",
    "topic",
    "topics",
    "question",
    "questions",
    "answer",
    "answers",
    "exercise",
    "exercises",
    "page",
    "pages",
    "notes",
    "study material",
    "content"
}


def _clean_topic_name(name: str) -> str:
    """
    Cleans a topic name returned by the AI.
    """

    name = str(name).strip()

    # Remove bullets/numbers at the beginning
    name = re.sub(
        r"^[\-\*\d\.\)\s]+",
        "",
        name
    )

    # Remove unnecessary trailing punctuation
    name = re.sub(
        r"[.:;,]+$",
        "",
        name
    )

    # Normalize whitespace
    name = re.sub(
        r"\s+",
        " ",
        name
    )

    return name.strip()


def _is_generic_topic(name: str) -> bool:
    """
    Returns True if the topic is too generic to be useful.
    """

    normalized = name.lower().strip()

    if normalized in GENERIC_TOPIC_WORDS:
        return True

    # Reject very short/generic single words
    if len(normalized.split()) == 1:
        generic_single_words = {
            "student",
            "class",
            "object",
            "method",
            "programming",
            "program",
            "example",
            "summary",
            "introduction",
            "chapter",
            "section",
            "topic",
            "notes"
        }

        if normalized in generic_single_words:
            return True

    return False


def _normalize_topic_objects(
    topics: list,
    max_topics: int = 12
) -> List[Dict[str, Any]]:
    """
    Converts raw AI topic objects into the format expected by
    the StudyFlow frontend.
    """

    cleaned = []
    seen = set()

    for item in topics:

        if isinstance(item, str):
            name = _clean_topic_name(item)

            importance = "medium"
            score = 5
            keywords = []

        elif isinstance(item, dict):

            name = _clean_topic_name(
                item.get(
                    "name",
                    item.get(
                        "topic",
                        ""
                    )
                )
            )

            importance = str(
                item.get(
                    "importance",
                    "medium"
                )
            ).lower().strip()

            try:
                score = int(
                    item.get(
                        "score",
                        5
                    )
                )
            except (TypeError, ValueError):
                score = 5

            keywords = item.get(
                "keywords",
                item.get(
                    "keywords_found",
                    []
                )
            )

            if not isinstance(keywords, list):
                keywords = []

            keywords = [
                str(k).strip()
                for k in keywords
                if str(k).strip()
            ]

        else:
            continue

        if not name:
            continue

        if _is_generic_topic(name):
            continue

        normalized_key = name.lower()

        if normalized_key in seen:
            continue

        seen.add(normalized_key)

        if importance not in {
            "high",
            "medium",
            "low"
        }:
            importance = "medium"

        score = max(
            1,
            min(
                10,
                score
            )
        )

        cleaned.append({
            "topic": name,
            "score": score,
            "importance": importance,
            "keywords_found": keywords
        })

    # Highest importance/score first
    importance_order = {
        "high": 0,
        "medium": 1,
        "low": 2
    }

    cleaned.sort(
        key=lambda x: (
            importance_order.get(
                x["importance"],
                1
            ),
            -x["score"]
        )
    )

    return cleaned[:max_topics]


def _ollama_extract_topics(
    text: str,
    max_topics: int = 12
) -> List[Dict[str, Any]]:
    """
    Uses local Ollama to extract meaningful academic topics.
    """

    if not text or not text.strip():
        return []

    # Give Ollama enough context while keeping response fast.
    source_text = text[:6000]

    system = """
You are an expert university study-material analyzer.

Your job is to identify the important academic concepts
that a student should actually study from the supplied material.

You must be selective.

Do NOT simply extract frequently occurring words.
Do NOT extract names of example variables, students,
or generic document headings.
"""

    prompt = f"""
Analyze the following study material.

SOURCE TEXT:
{source_text}

Extract the MAIN STUDY TOPICS.

STRICT RULES:

1. Extract only meaningful academic concepts discussed
   in the source.

2. Prefer:
   - definitions
   - principles
   - theories
   - mechanisms
   - techniques
   - classifications
   - important concepts
   - important processes

3. Do NOT return generic words such as:
   - Class
   - Object
   - Method
   - Student
   - Programming
   - Program
   - Example
   - Introduction
   - Summary
   - Conclusion
   - Key Takeaway
   - Chapter
   - Section
   - Topic

4. Do NOT return names of people, students, variables,
   fictional/example entities, or document metadata.

5. Combine closely related concepts when appropriate.

   Example:
   "Class" + "Object"
   should become:
   "Classes and Objects"

6. Preserve important terminology from the source.

7. Do not invent concepts that are not present
   in the source.

8. Return between 5 and {max_topics} useful topics
   if enough meaningful topics exist.

9. Topic names should normally contain 2 to 6 words.

10. Assign importance:
    - high = major/core concept
    - medium = supporting concept
    - low = minor concept

11. Give a score from 1 to 10:
    - 9-10 = very important core topic
    - 7-8 = important topic
    - 4-6 = supporting topic
    - 1-3 = minor topic

12. Include keywords that actually occur in the source.

13. Return ONLY valid JSON.
    No markdown.
    No explanation.
    No extra text.

Required format:

{{
  "topics": [
    {{
      "name": "Classes and Objects",
      "importance": "high",
      "score": 10,
      "keywords": ["class", "object"]
    }}
  ]
}}
"""

    response = query_ollama(
        prompt,
        system=system,
        timeout=60.0
    )

    if not response:
        return []

    try:
        # First try parsing the complete response.
        parsed = json.loads(response)

    except json.JSONDecodeError:

        # If Ollama accidentally added text around JSON,
        # extract the JSON object.
        try:
            match = re.search(
                r"\{.*\}",
                response,
                re.DOTALL
            )

            if not match:
                return []

            parsed = json.loads(
                match.group(0)
            )

        except Exception:
            return []

    if isinstance(parsed, dict):
        topics = parsed.get(
            "topics",
            []
        )
    elif isinstance(parsed, list):
        topics = parsed
    else:
        return []

    if not isinstance(topics, list):
        return []

    return _normalize_topic_objects(
        topics,
        max_topics=max_topics
    )


def _fallback_extract_topics(
    text: str,
    max_topics: int = 12
) -> List[Dict[str, Any]]:
    """
    Offline fallback when Ollama is unavailable.

    Uses known academic domains and document headings.
    """

    if not text:
        return []

    text_lower = text.lower()

    # --------------------------------------------------------
    # 1. Known academic domain matching
    # --------------------------------------------------------

    for item in KNOWN_TOPIC_SETS:

        matches = sum(
            1
            for keyword in item["keywords"]
            if keyword in text_lower
        )

        if matches >= 3:

            result = []

            for index, topic in enumerate(
                item["topics"]
            ):

                result.append({
                    "topic": topic,
                    "score": max(
                        6,
                        10 - index
                    ),
                    "importance": (
                        "high"
                        if index < 2
                        else "medium"
                    ),
                    "keywords_found": []
                })

            return result[:max_topics]

    # --------------------------------------------------------
    # 2. Extract useful headings
    # --------------------------------------------------------

    extracted = []

    lines = text.splitlines()

    for line in lines:

        line_s = line.strip()

        if not line_s:
            continue

        # Remove numbering such as:
        # 1.
        # 1)
        # 1.1
        clean = re.sub(
            r"^\d+(?:\.\d+)*[\.\)\-:]?\s*",
            "",
            line_s
        )

        # Remove heading prefixes
        clean = re.sub(
            r"^(chapter|section|unit|module|topic)\s*(\d+)?\s*[:.-]?\s*",
            "",
            clean,
            flags=re.IGNORECASE
        )

        clean = clean.strip()

        if not clean:
            continue

        if len(clean) < 4 or len(clean) > 80:
            continue

        if _is_generic_topic(clean):
            continue

        # Prefer lines that look like headings.
        words = clean.split()

        looks_like_heading = (
            len(words) <= 10
            and (
                clean.isupper()
                or clean.istitle()
                or ":" in line_s
            )
        )

        if looks_like_heading:

            topic = _clean_topic_name(clean)

            if topic.lower() not in {
                x["topic"].lower()
                for x in extracted
            }:

                extracted.append({
                    "topic": topic,
                    "score": 7,
                    "importance": "medium",
                    "keywords_found": []
                })

        if len(extracted) >= max_topics:
            break

    if extracted:
        return extracted[:max_topics]

    # --------------------------------------------------------
    # 3. Generic fallback
    # --------------------------------------------------------

    return [
        {
            "topic": "General Concepts",
            "score": 5,
            "importance": "medium",
            "keywords_found": []
        }
    ]


def extract_topics(
    text: str,
    max_topics: int = 12
) -> List[Dict[str, Any]]:
    """
    Extracts meaningful study topics.

    Uses local Ollama first and then falls back
    to a deterministic heuristic engine.
    """

    if not text or len(text.strip()) < 20:

        return [
            {
                "topic": "General Concepts",
                "score": 5,
                "importance": "medium",
                "keywords_found": []
            }
        ]

    # Try local Ollama first.
    if check_ollama():

        topics = _ollama_extract_topics(
            text,
            max_topics=max_topics
        )

        if len(topics) >= 3:
            return topics

    # Fallback
    return _fallback_extract_topics(
        text,
        max_topics=max_topics
    )


# ============================================================
# 2. STUDY PLAN GENERATION
# ============================================================

def generate_study_plan(
    topics: List[str],
    exam_date_str: str,
    hours_per_day: float = 1.5
) -> List[Dict[str, Any]]:
    """
    Generates a personalized day-by-day study schedule.
    """

    if not topics:
        topics = [
            "General Concepts"
        ]

    today = date.today()

    days_count = 7

    try:

        if exam_date_str:

            exam_d = datetime.strptime(
                exam_date_str,
                "%Y-%m-%d"
            ).date()

            diff = (
                exam_d - today
            ).days

            if diff >= 2:
                days_count = min(
                    max(diff, 3),
                    14
                )
            else:
                days_count = 7

    except Exception:
        days_count = 7

    total_mins = max(
        int(hours_per_day * 60),
        30
    )

    topic_mins = min(
        max(
            int(total_mins * 0.75),
            30
        ),
        90
    )

    # --------------------------------------------------------
    # Ollama study plan
    # --------------------------------------------------------

    if check_ollama():

        system = """
You are a personalized university study coach.

Create a realistic study plan from the supplied topics.

Output ONLY a valid JSON array.
No markdown.
No explanations.
"""

        prompt = f"""
Topics:
{", ".join(topics)}

Days until exam:
{days_count}

Hours per day:
{hours_per_day}

Create a study plan.

Each item must contain:

{{
  "day": 1,
  "topic": "Topic name",
  "duration": "45 minutes",
  "description": "What the student should study"
}}

Include:
- all important topics
- revision
- final practice/quiz
"""

        resp = query_ollama(
            prompt,
            system=system,
            timeout=30.0
        )

        if resp:

            try:

                match = re.search(
                    r"\[.*\]",
                    resp,
                    re.DOTALL
                )

                if match:

                    parsed = json.loads(
                        match.group(0)
                    )

                    plan = []

                    for i, item in enumerate(parsed):

                        plan.append({
                            "id": f"task-{i + 1}",
                            "day": item.get(
                                "day",
                                i + 1
                            ),
                            "topic": item.get(
                                "topic",
                                f"Topic {i + 1}"
                            ),
                            "duration": item.get(
                                "duration",
                                f"{topic_mins} minutes"
                            ),
                            "description": item.get(
                                "description",
                                "Review concepts, take notes, and solve practice problems."
                            ),
                            "completed": False,
                            "type": (
                                "revision"
                                if "revision" in str(
                                    item.get(
                                        "topic",
                                        ""
                                    )
                                ).lower()
                                else (
                                    "quiz"
                                    if "quiz" in str(
                                        item.get(
                                            "topic",
                                            ""
                                        )
                                    ).lower()
                                    else "study"
                                )
                            )
                        })

                    if len(plan) >= 3:
                        return plan

            except Exception:
                pass

    # --------------------------------------------------------
    # Heuristic study plan
    # --------------------------------------------------------

    plan = []

    num_topics = len(topics)

    has_revision_days = days_count >= 4

    study_days = (
        days_count - 2
        if has_revision_days
        else days_count
    )

    for day_idx in range(study_days):

        topic_idx = (
            day_idx % num_topics
        )

        topic = topics[topic_idx]

        day_num = day_idx + 1

        dur = f"{topic_mins} minutes"

        desc = (
            f"Deep dive into {topic} "
            f"fundamentals, key definitions, "
            f"and important concepts."
        )

        if day_idx >= num_topics:

            dur = (
                f"{max(30, topic_mins - 15)} minutes"
            )

            desc = (
                f"Second-pass review and exercises "
                f"on {topic}."
            )

        plan.append({
            "id": f"task-{day_num}",
            "day": day_num,
            "topic": topic,
            "duration": dur,
            "description": desc,
            "completed": False,
            "type": "study"
        })

    if has_revision_days:

        rev_day = study_days + 1

        plan.append({
            "id": f"task-{rev_day}",
            "day": rev_day,
            "topic": "Revision and Key Concepts",
            "duration": f"{total_mins} minutes",
            "description": (
                "Review important definitions, "
                "concepts, comparisons, and weak areas."
            ),
            "completed": False,
            "type": "revision"
        })

        quiz_day = study_days + 2

        plan.append({
            "id": f"task-{quiz_day}",
            "day": quiz_day,
            "topic": "Mock Quiz and Final Preparation",
            "duration": "30 minutes",
            "description": (
                "Attempt practice questions and "
                "review mistakes before the exam."
            ),
            "completed": False,
            "type": "quiz"
        })

    return plan


# ============================================================
# 3. QUIZ GENERATION
# ============================================================

QUESTION_BANK = {

    "OSI Model": [
        {
            "question": "Which layer of the OSI model is responsible for packet routing and logical IP addressing?",
            "options": [
                "Transport Layer",
                "Network Layer",
                "Session Layer",
                "Presentation Layer"
            ],
            "answer": "B",
            "explanation": "The Network layer handles logical addressing and packet routing."
        },

        {
            "question": "At which OSI layer does MAC addressing and frame error detection occur?",
            "options": [
                "Physical Layer",
                "Data Link Layer",
                "Transport Layer",
                "Application Layer"
            ],
            "answer": "B",
            "explanation": "The Data Link layer handles frames and MAC addressing."
        },

        {
            "question": "Which OSI layer provides data encryption, compression, and character code translation?",
            "options": [
                "Application Layer",
                "Presentation Layer",
                "Session Layer",
                "Transport Layer"
            ],
            "answer": "B",
            "explanation": "The Presentation layer handles data representation, encryption, and compression."
        },

        {
            "question": "Which layer is responsible for end-to-end communication and reliable delivery such as TCP?",
            "options": [
                "Network Layer",
                "Transport Layer",
                "Physical Layer",
                "Session Layer"
            ],
            "answer": "B",
            "explanation": "The Transport layer provides end-to-end communication."
        },

        {
            "question": "How many layers are defined in the standard OSI reference model?",
            "options": [
                "4",
                "5",
                "7",
                "8"
            ],
            "answer": "C",
            "explanation": "The OSI reference model consists of seven layers."
        }
    ],

    "TCP/IP": [
        {
            "question": "How many layers are commonly defined in the TCP/IP model?",
            "options": [
                "3",
                "4",
                "6",
                "7"
            ],
            "answer": "B",
            "explanation": "The commonly taught TCP/IP model has four layers."
        },

        {
            "question": "Which protocol uses a three-way handshake?",
            "options": [
                "UDP",
                "TCP",
                "ICMP",
                "IP"
            ],
            "answer": "B",
            "explanation": "TCP establishes connections using SYN, SYN-ACK, and ACK."
        },

        {
            "question": "Which TCP/IP layer handles IP addressing and routing?",
            "options": [
                "Application Layer",
                "Internet Layer",
                "Transport Layer",
                "Network Access Layer"
            ],
            "answer": "B",
            "explanation": "The Internet layer handles IP addressing and routing."
        },

        {
            "question": "Which transport protocol is connectionless?",
            "options": [
                "TCP",
                "FTP",
                "UDP",
                "HTTP"
            ],
            "answer": "C",
            "explanation": "UDP is a connectionless transport protocol."
        },

        {
            "question": "What is the primary function of ICMP?",
            "options": [
                "File transfer",
                "Error reporting and network diagnostics",
                "Domain name lookup",
                "Data encryption"
            ],
            "answer": "B",
            "explanation": "ICMP is used for network error reporting and diagnostics."
        }
    ],

    "Network Devices": [
        {
            "question": "Which device operates primarily at OSI Layer 2 and uses MAC address tables?",
            "options": [
                "Repeater",
                "Switch",
                "Hub",
                "Gateway"
            ],
            "answer": "B",
            "explanation": "A switch forwards frames using MAC addresses."
        },

        {
            "question": "Why is a hub less efficient than a switch?",
            "options": [
                "It encrypts all data packets",
                "It broadcasts incoming signals to all ports",
                "It only supports wireless connections",
                "It requires manual routing tables"
            ],
            "answer": "B",
            "explanation": "A hub broadcasts incoming signals to all ports."
        },

        {
            "question": "Which device connects different IP subnets?",
            "options": [
                "Modem",
                "Switch",
                "Router",
                "Access Point"
            ],
            "answer": "C",
            "explanation": "Routers connect networks and route packets between them."
        },

        {
            "question": "Which security device filters network traffic using security rules?",
            "options": [
                "Hub",
                "Firewall",
                "Repeater",
                "Bridge"
            ],
            "answer": "B",
            "explanation": "A firewall filters network traffic according to security rules."
        },

        {
            "question": "What is the purpose of a default gateway?",
            "options": [
                "To assign MAC addresses",
                "To route traffic to external networks",
                "To convert analog signals to digital",
                "To serve web pages"
            ],
            "answer": "B",
            "explanation": "The default gateway provides a route outside the local network."
        }
    ],

    "Network Topologies": [
        {
            "question": "In which topology are all nodes connected to a central device?",
            "options": [
                "Bus Topology",
                "Star Topology",
                "Ring Topology",
                "Mesh Topology"
            ],
            "answer": "B",
            "explanation": "Star topology connects nodes to a central switch or hub."
        },

        {
            "question": "What is a major disadvantage of a Bus topology?",
            "options": [
                "Extremely high cabling cost",
                "A backbone failure can disrupt the network",
                "Requires a powerful central server",
                "Cannot connect more than three computers"
            ],
            "answer": "B",
            "explanation": "A bus topology depends on a shared backbone cable."
        },

        {
            "question": "In a full mesh topology with n devices, how many links are required?",
            "options": [
                "n - 1",
                "n * (n - 1) / 2",
                "n^2",
                "2n"
            ],
            "answer": "B",
            "explanation": "A full mesh requires n(n-1)/2 links."
        },

        {
            "question": "Which topology provides high redundancy through multiple direct connections?",
            "options": [
                "Bus",
                "Star",
                "Full Mesh",
                "Ring"
            ],
            "answer": "C",
            "explanation": "Full mesh provides multiple direct paths between devices."
        },

        {
            "question": "Which topology combines two or more different topologies?",
            "options": [
                "Hybrid Topology",
                "Token Ring",
                "Peer-to-Peer",
                "Dual Ring"
            ],
            "answer": "A",
            "explanation": "A hybrid topology combines different topology types."
        }
    ],

    "Protocols": [
        {
            "question": "Which protocol automatically assigns IP addresses to client devices?",
            "options": [
                "DNS",
                "DHCP",
                "SNMP",
                "SMTP"
            ],
            "answer": "B",
            "explanation": "DHCP automatically provides IP configuration to clients."
        },

        {
            "question": "What is the primary role of DNS?",
            "options": [
                "Encrypting email messages",
                "Resolving domain names to IP addresses",
                "Filtering spam packets",
                "Measuring packet round-trip time"
            ],
            "answer": "B",
            "explanation": "DNS resolves domain names into IP addresses."
        },

        {
            "question": "Which protocol provides secure web browsing?",
            "options": [
                "HTTP",
                "HTTPS",
                "FTP",
                "Telnet"
            ],
            "answer": "B",
            "explanation": "HTTPS provides encrypted web communication using TLS."
        },

        {
            "question": "Which protocol maps an IPv4 address to a MAC address?",
            "options": [
                "ARP",
                "RARP",
                "NAT",
                "BGP"
            ],
            "answer": "A",
            "explanation": "ARP resolves IPv4 addresses to MAC addresses on a local network."
        },

        {
            "question": "Which port is commonly used by HTTP?",
            "options": [
                "21",
                "22",
                "53",
                "80"
            ],
            "answer": "D",
            "explanation": "HTTP commonly uses TCP port 80."
        }
    ]
}


def generate_quiz(
    text: str,
    topic: str = "All Topics",
    num_questions: int = 5
) -> List[Dict[str, Any]]:
    """
    Generates multiple-choice quiz questions.

    Uses Ollama first and then the local question bank.
    """

    num_questions = min(
        max(num_questions, 1),
        10
    )

    # --------------------------------------------------------
    # Ollama quiz generation
    # --------------------------------------------------------

    if check_ollama() and text and len(text) > 50:

        system = f"""
You are a university examiner.

Create {num_questions} multiple-choice questions based
ONLY on the supplied study material.

Output ONLY a JSON array.

Each question must contain:

"question": string
"options": exactly 4 strings
"answer": "A", "B", "C", or "D"
"explanation": short explanation
"topic": "{topic}"

Do not add markdown.
Do not add any other text.
"""

        prompt = f"""
Study Material:

{text[:4000]}

Generate {num_questions} questions.
"""

        resp = query_ollama(
            prompt,
            system=system,
            timeout=45.0
        )

        if resp:

            try:

                match = re.search(
                    r"\[.*\]",
                    resp,
                    re.DOTALL
                )

                if match:

                    parsed = json.loads(
                        match.group(0)
                    )

                    questions = []

                    for i, q in enumerate(parsed):

                        opts = q.get(
                            "options",
                            []
                        )

                        if (
                            isinstance(opts, list)
                            and len(opts) == 4
                            and q.get("answer")
                            in ["A", "B", "C", "D"]
                        ):

                            questions.append({
                                "id": f"q{i + 1}",
                                "topic": q.get(
                                    "topic",
                                    topic
                                    if topic != "All Topics"
                                    else "General"
                                ),
                                "question": q.get(
                                    "question",
                                    ""
                                ),
                                "options": opts,
                                "answer": q.get(
                                    "answer",
                                    "A"
                                ),
                                "explanation": q.get(
                                    "explanation",
                                    "Reference from study material."
                                )
                            })

                    if len(questions) >= 1:
                        return questions[:num_questions]

            except Exception:
                pass

    # --------------------------------------------------------
    # Question bank fallback
    # --------------------------------------------------------

    candidate_questions = []

    if topic and topic != "All Topics":

        matched_key = None

        for key in QUESTION_BANK:

            if (
                key.lower() in topic.lower()
                or topic.lower() in key.lower()
            ):
                matched_key = key
                break

        if matched_key:

            candidate_questions = list(
                QUESTION_BANK[matched_key]
            )

        else:

            for key, qlist in QUESTION_BANK.items():

                for q in qlist:

                    candidate_questions.append({
                        **q,
                        "topic": topic
                    })

    else:

        for key, qlist in QUESTION_BANK.items():

            for q in qlist:

                candidate_questions.append({
                    **q,
                    "topic": key
                })

    random.shuffle(candidate_questions)

    selected = candidate_questions[
        :num_questions
    ]

    result = []

    for i, q in enumerate(selected):

        result.append({
            "id": f"q{i + 1}",
            "topic": q.get(
                "topic",
                topic
            ),
            "question": q["question"],
            "options": q["options"],
            "answer": q["answer"],
            "explanation": q.get(
                "explanation",
                "Standard foundational definition."
            )
        })

    return result


# ============================================================
# 4. QUIZ ANALYSIS & RECOMMENDATIONS
# ============================================================

def analyze_quiz(
    questions: List[Dict[str, Any]],
    user_answers: Dict[str, str]
) -> Dict[str, Any]:
    """
    Scores the submitted quiz, identifies strong and weak
    topics, and returns a recommendation.
    """

    total = len(questions)

    if total == 0:

        return {
            "score": 0,
            "total": 0,
            "percentage": 0,
            "strong_topics": [],
            "weak_topics": [],
            "recommendation": (
                "Please complete a quiz to see your analysis."
            ),
            "breakdown": []
        }

    correct_count = 0

    topic_stats: Dict[
        str,
        Dict[str, int]
    ] = {}

    breakdown = []

    for q in questions:

        qid = q["id"]

        topic = q.get(
            "topic",
            "General Concept"
        )

        correct_ans = q.get(
            "answer",
            ""
        ).strip().upper()

        user_ans = user_answers.get(
            qid,
            ""
        ).strip().upper()

        is_correct = (
            user_ans == correct_ans
            and user_ans != ""
        )

        if is_correct:
            correct_count += 1

        if topic not in topic_stats:

            topic_stats[topic] = {
                "correct": 0,
                "total": 0
            }

        topic_stats[topic]["total"] += 1

        if is_correct:
            topic_stats[topic]["correct"] += 1

        breakdown.append({
            "id": qid,
            "question": q.get(
                "question"
            ),
            "topic": topic,
            "user_answer": (
                user_ans
                or "None"
            ),
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "explanation": q.get(
                "explanation",
                ""
            )
        })

    percentage = round(
        (correct_count / total) * 100
    )

    strong_topics = []
    weak_topics = []

    for topic, stats in topic_stats.items():

        accuracy = (
            stats["correct"]
            / stats["total"]
        )

        if accuracy >= 0.7:

            strong_topics.append(topic)

        else:

            weak_topics.append(topic)

    # --------------------------------------------------------
    # AI recommendation
    # --------------------------------------------------------

    recommendation = ""

    if check_ollama():

        system = """
You are an encouraging academic tutor.

Write a concise 1-2 sentence recommendation
for a university student based on their quiz result.

Mention specific topics that need revision.

Do not exaggerate.
"""

        prompt = f"""
Score:
{correct_count}/{total}
({percentage}%)

Strong topics:
{", ".join(strong_topics) or "None"}

Topics needing practice:
{", ".join(weak_topics) or "None"}

Provide a recommendation.
"""

        resp = query_ollama(
            prompt,
            system=system,
            timeout=20.0
        )

        if resp:
            recommendation = (
                resp.strip()
                .strip('"')
            )

    if not recommendation:

        if strong_topics and weak_topics:

            recommendation = (
                f"You performed well on "
                f"{', '.join(strong_topics)} "
                f"but need more practice with "
                f"{', '.join(weak_topics)}."
            )

        elif weak_topics:

            recommendation = (
                f"Review the core concepts in "
                f"{', '.join(weak_topics)} "
                f"and attempt another practice quiz."
            )

        elif strong_topics:

            recommendation = (
                f"You demonstrated good understanding "
                f"across the tested topics, including "
                f"{', '.join(strong_topics)}."
            )

        else:

            recommendation = (
                "Review the questions you missed "
                "and continue with your study plan."
            )

    return {
        "score": correct_count,
        "total": total,
        "percentage": percentage,
        "strong_topics": strong_topics,
        "weak_topics": weak_topics,
        "recommendation": recommendation,
        "breakdown": breakdown
    }