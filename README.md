# 🚀 ELEVORA AI — Learn-to-Earn Career Platform
### *Turn your potential into opportunity.*

[![Hackathon Domain: LearnSphere AI](https://img.shields.io/badge/Hackathon%20Domain-LearnSphere%20AI-7557E8?style=for-the-badge)](https://elevora.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-24A47A?style=for-the-badge)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge)](https://python.org)
[![Tech Stack: Zero-Dependency Server](https://img.shields.io/badge/Stack-Python%20%7C%20SQLite%20%7C%20Vanilla%20ES6%20%7C%20Tailwind-987BFF?style=for-the-badge)](https://elevora.ai)

---

## 🌟 Executive Summary

**Elevora AI** is a complete, modern, responsive web application built for the **LearnSphere AI Hackathon**.

Most career platforms, online courses, project showcases, and job portals operate in silos:
* Students get stuck in **Tutorial Hell** without knowing what skills employers actually require.
* Unverified resumes claim technical keywords with **no proof of implementation**.
* Job portals issue automated rejections **without actionable feedback** on which skill gaps need bridging.

**Elevora AI bridges these activities into one unified Learn-to-Prove-to-Earn pathway:**

```
Learn what matters ──▶ Build something practical ──▶ Prove what you can do ──▶ Discover opportunities
```

---

## 🎯 The Main Differentiator — Our X-Factor

The core innovation of Elevora AI is the **Learn-to-Prove-to-Earn Pipeline**:

1. **Target Career Selection:** Students select their focus (MVP role: **Frontend Developer**).
2. **Job Market Skill Analysis:** Elevora analyzes a curated benchmark dataset of industry job descriptions to identify essential vs. preferred skills.
3. **AI Skill-Gap Identification:** Compares the student's current skills against market demand using a transparent mathematical scoring algorithm.
4. **Personalized Learning Roadmap:** Generates a structured 5-stage roadmap linked to genuine, free, high-quality documentation (MDN Web Docs, freeCodeCamp, JavaScript.info, official React docs).
5. **Practical Project Assignment:** Assigns a real-world capstone project (*Interactive Task Management Web Application*).
6. **AI Rubric Evaluation:** Grades submitted deliverables (live demo URL, GitHub repo, architecture notes) across **6 transparent rubric criteria** (/60 points).
7. **Demonstrated Skill Profile:** Automatically upgrades verified abilities from "In Progress" to "Demonstrated & Verified".
8. **Dynamic Opportunity Matching:** Matched internships and entry-level positions update their match percentages in real time as the student proves their skills (e.g. jumping from **52% to 92%**).

---

## 🏗️ Architecture & Technology Stack

Designed for maximum reliability, speed, zero dependency bloat, and instantaneous hackathon evaluation:

* **Backend (`server.py`):**
  * Built using Python 3's standard library (`http.server.ThreadingHTTPServer`, `sqlite3`, `json`, `urllib`).
  * **Requires zero pip package installations.** Runs out of the box on Windows, macOS, and Linux.
  * REST API endpoints with full CORS support and SPA static file routing.
* **Database (`database.py`):**
  * SQLite persistence (`elevora.db` / system temp fallback for OneDrive).
  * Auto-initialization and seeded with realistic demo data, benchmark jobs, roadmap stages, and user profiles.
* **AI Service Layer (`ai_service.py`):**
  * Supports **Google Gemini API** (`gemini-1.5-flash`) through backend calls.
  * **Robust Heuristic Fallback Engine:** If no API key is supplied or network is unavailable, generates transparent, rubric-based feedback and advice with zero mock text.
* **Frontend (`static/`):**
  * Single Page Application (SPA) with responsive client-side router.
  * Tailwind CSS design system with the Elevora Brand Palette:
    * **Deep Midnight Navy:** `#101426`
    * **Primary Purple:** `#7557E8`
    * **Electric Violet:** `#987BFF`
    * **Soft Lavender:** `#EDE8FF`
    * **Surface Background:** `#F7F7FC`
    * **Dark Text:** `#20243A`
    * **Success Green:** `#24A47A`
  * Lucide Icons & Canvas Confetti for milestone celebrations.
  * Dual-mode client store (`data.js`) providing zero-downtime LocalStorage persistence.

---

## 📁 Project Folder Structure

```
elevora-ai/
├── server.py              # Multi-threaded HTTP & REST API server (Standard Library)
├── database.py            # SQLite database schema, initialization & seed dataset
├── ai_service.py          # Google Gemini LLM API integration & heuristic rubric engine
├── test_backend.py        # Automated verification test suite (100% pass rate)
├── .env.example           # Environment template (API keys, ports)
├── README.md              # Comprehensive documentation and demo walkthrough
└── static/                # Single Page Application frontend
    ├── index.html         # HTML5 entry point & sticky Judge Demo Controller
    ├── css/
    │   └── style.css      # Elevora design system, custom utilities & glassmorphism
    └── js/
        ├── app.js         # Master router, state management & view renderers
        └── data.js        # Benchmark datasets, transparent math & local store
```

---

## ⚡ Quick Start & Running Locally

### Prerequisites
* **Python 3.10+** (Tested and verified on Python 3.14).
* No external package managers or compilers required!

### 1. Start the Application Server
Run the single command in your terminal from the project folder:

```bash
python server.py
```

Output:
```text
==================================================================
  ELEVORA AI - Learn-to-Prove-to-Earn Career Platform
  Turn your potential into opportunity.
==================================================================
  Local URL:        http://localhost:8000
  Network URL:      http://127.0.0.1:8000
  Demo Account:     demo@elevora.ai  (password: elevora2026)
==================================================================
```

### 2. Open in Your Browser
Navigate to:
👉 **`http://localhost:8000`**

*(Alternatively, you can also double-click `static/index.html` directly in your browser. The application includes a self-contained client-side data engine that operates 100% interactively even without the server running!)*

---

## 🔑 Optional: Connecting Google Gemini API

Elevora AI includes an intelligent rule-based heuristic evaluator that works offline with zero configuration. To activate live dynamic LLM responses:

1. Copy the example configuration:
   ```bash
   cp .env.example .env
   ```
2. Get an API key from [Google AI Studio](https://aistudio.google.com/).
3. Set your key in `.env`:
   ```ini
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-1.5-flash
   ```
4. Restart `python server.py`. All career advisor queries will now dynamically query Gemini!

---

## 🧪 Automated Test Suite

Verify all database tables, seed records, REST endpoints, and mathematical formulas:

```bash
python test_backend.py
```

Expected output:
```text
>>> 1. Testing Database Initialization...
   ✓ Demo user Alex Chen verified.
   ✓ User skills verified (5 skills found).
   ✓ Job listings verified (5 jobs found).
   ✓ Learning roadmap verified (8 lessons found).

>>> 2. Testing Skill-Gap Analysis Algorithm...
   ✓ Initial Match Score: 70.0%
   ✓ Initial Career Readiness: 65.0%

>>> 3. Testing Practical Project & Rubric Evaluation...
   ✓ Rubric Score: 54/60 (90.0%) - Grade: A+ (Workforce Ready)
   ✓ Unlocked Demonstrated Skills: ['JavaScript', 'Responsive Design', 'Git & GitHub', 'Web Storage API']

>>> 4. Testing Rule-Based Career Advisory Fallback...
   ✓ Career Advisor response generated cleanly.

>>> 5. Testing Demo Reset...
   ✓ Demo reset successfully verified.

========================================================
 ALL BACKEND & LOGIC VERIFICATION CHECKS PASSED (100%) 
========================================================
```

---

## 🏆 The Hackathon Demonstration Journey (Steps 1–9)

We have built a dedicated **Judge Demo Tour Bar** pinned to the top of the application so evaluators can test the complete end-to-end journey in under 3 minutes:

### 👤 Demo Persona:
* **Name:** Alex Chen
* **Education:** 3rd Year CSE Undergraduate Student
* **Target Role:** Frontend Developer
* **Starting Profile:** Knows semantic HTML5 & responsive CSS3; lacks JavaScript state experience and practical project portfolio.

### 🚶 Guided 9-Step Pathway:

| Step | Action | What Judges See |
|:---:|:---|:---|
| **Step 1** | Click **"1. Profile"** | **Profile & Target Role:** View Alex's starting state. Target: Frontend Developer. Starting Readiness: ~55%. |
| **Step 2** | Click **"2. Market"** | **Job Market Analyzer:** 5 benchmark vacancies analyzed. JavaScript (100%), HTML/CSS (100%), Git (80%), React (60%). |
| **Step 3** | Click **"3. Skill Gaps"** | **AI Skill-Gap Report:** JavaScript and Git diagnosed as high-priority missing skills with transparent math formula. |
| **Step 4** | Click **"4. Roadmap"** | **Personalized Roadmap:** 5-stage curriculum with genuine documentation links (MDN, freeCodeCamp, React). Toggle lessons to see progress update live. |
| **Step 5** | Click **"5. Project"** | **Practical Capstone:** Assigned *Interactive Task Management Web Application* with 4 milestone checklists. |
| **Step 6** | Click **"6. Evaluate"** | **Submit & Rubric Evaluation:** Deliverables submitted. Rubric engine scores 6 criteria (/60 pts) $\rightarrow$ **Grade A+ (90%)**. Confetti celebration! |
| **Step 7** | Click **"7. Skills"** | **Demonstrated Skills:** JavaScript and Responsive Design automatically upgrade to *Proven via Capstone* in the 3-tier skill inventory. |
| **Step 8** | Click **"8. Opportunities"** | **Opportunity Matching:** Watch match percentage for *CloudScale Junior Frontend Intern* leap from **52% to 92%**! Click *Apply Now* to transmit dossier. |
| **Step 9** | Click **"9. Portfolio"** | **Public Shareable Portfolio:** Generate shareable portfolio link with rubric grades, verified badges, and live demo link. |

*At any point, click **"Reset Demo"** in the top bar to restart the scenario from Step 1.*

---

## 📊 Transparent Mathematical Formulas

Elevora AI avoids arbitrary percentages. All metrics are derived from transparent, documented rules:

$$\text{Skill Match Score} = \left(\frac{\text{Matched Essential}}{\text{Total Essential}} \times 70\%\right) + \left(\frac{\text{Matched Preferred}}{\text{Total Preferred}} \times 30\%\right)$$

$$\text{Overall Career Readiness} = (\text{Skill Match Score} \times 0.5) + \left(\frac{\text{Demonstrated Skills}}{\text{Total Essential}} \times 50\%\right)$$

---

## 🌐 Deployment Instructions

Elevora AI is production-ready for deployment to any cloud environment:

### Deploy to Render / Railway / Heroku
1. Push this repository to GitHub.
2. Create a new **Web Service**.
3. Set the start command:
   ```bash
   python server.py
   ```
4. Set the environment variable:
   ```ini
   PORT=8000
   ```
5. (Optional) Set `GEMINI_API_KEY`.

### Deploy Frontend Statically (Vercel / Netlify / GitHub Pages)
The contents of the `static/` directory can be deployed directly to Vercel, Netlify, or GitHub Pages. The client-side fallback store in `data.js` ensures all 7 core modules work smoothly even on static hosting!

---

## ⚖️ Ethics & Data Transparency

* **Curated Benchmark Data:** All vacancies, company profiles, and listings are curated benchmark models designed for educational simulation.
* **No Exaggerated Claims:** Elevora does not promise guaranteed employment or claim to certify professional competence; it acts as an evidence-based roadmap and portfolio accelerator.
* **Security & Privacy:** API keys are never exposed in frontend code; all LLM calls originate through the backend.

---

**ELEVORA AI — Turn your potential into opportunity.**
*Built with ❤️ for the LearnSphere AI Hackathon 2026.*
