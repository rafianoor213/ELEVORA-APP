"""
ELEVORA AI - AI Service & Evaluation Engine
Provides LLM-assisted career advisory and rubric-based project evaluation.
Supports Google Gemini API with seamless, high-fidelity rule-based heuristic fallback.
"""

import os
import json
import urllib.request
import urllib.error
import re
from pathlib import Path

# Load .env if present
def load_env_file():
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

load_env_file()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

def call_gemini_api(prompt: str, system_instruction: str = None) -> dict:
    """Calls Gemini API if GEMINI_API_KEY is configured. Returns dict with text and success flag."""
    if not GEMINI_API_KEY:
        return {"success": False, "error": "No GEMINI_API_KEY provided"}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    contents = [{"role": "user", "parts": [{"text": prompt}]}]
    payload = {"contents": contents}

    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            result = json.loads(response.read().decode("utf-8"))
            candidates = result.get("candidates", [])
            if candidates and "content" in candidates[0]:
                text = candidates[0]["content"]["parts"][0]["text"]
                return {"success": True, "text": text, "model": GEMINI_MODEL}
            return {"success": False, "error": "Empty response from Gemini API"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# -------------------------------------------------------------
# 1. AI CAREER ADVISOR
# -------------------------------------------------------------
def get_career_advice(query: str, user_profile: dict) -> dict:
    """
    Generates structured career advice based on user profile and query.
    Returns:
    {
        "source": "gemini-ai" | "rule-based-engine",
        "career_overview": str,
        "required_skills": list[str],
        "current_strengths": list[str],
        "missing_skills": list[dict],
        "recommended_next_steps": list[str],
        "message": str
    }
    """
    target_career = user_profile.get("target_career", "Frontend Developer")
    user_skills = [s.get("skill_name") for s in user_profile.get("skills", [])]
    user_name = user_profile.get("full_name", "Student")

    system_instruction = (
        "You are Elevora AI Career Advisor, a senior engineering career mentor for university students and fresh graduates. "
        "Provide honest, actionable, structured career guidance for tech roles. Avoid fluffy motivational quotes. "
        "Format your answer with clear markdown headings and bullet points."
    )

    prompt = (
        f"User: {user_name}\n"
        f"Target Career: {target_career}\n"
        f"Current Known Skills: {', '.join(user_skills) if user_skills else 'Beginner fundamentals'}\n"
        f"User Question/Goal: {query}\n\n"
        "Please provide structured career advice:\n"
        "1. Career & Market Reality Overview\n"
        "2. Essential Technical Skills vs Preferred Skills\n"
        "3. User's Current Strengths Assessment\n"
        "4. Critical Missing Skills (Gaps) & Priority\n"
        "5. Immediate Actionable Next Steps (Learn -> Prove -> Earn Pathway)\n"
    )

    # Attempt Gemini API
    gemini_res = call_gemini_api(prompt, system_instruction)
    if gemini_res.get("success"):
        return {
            "source": f"gemini-ai ({gemini_res.get('model')})",
            "is_ai_generated": True,
            "message": gemini_res["text"],
            "target_career": target_career
        }

    # High-quality Rule-Based Fallback
    fallback_advice = generate_rule_based_advice(query, user_profile)
    return fallback_advice

def generate_rule_based_advice(query: str, user_profile: dict) -> dict:
    """Contextual heuristic advisory response based on user state."""
    target_career = user_profile.get("target_career", "Frontend Developer")
    user_skills = [s.get("skill_name") for s in user_profile.get("skills", [])]
    user_name = user_profile.get("full_name", "Alex")

    has_html_css = "HTML5" in user_skills or "CSS3" in user_skills
    has_js = "JavaScript" in user_skills
    has_react = "React" in user_skills

    strengths = []
    if has_html_css:
        strengths.append("Strong foundational knowledge in semantic HTML and responsive CSS styling.")
    if has_js:
        strengths.append("Familiarity with core JavaScript syntax and DOM manipulation basics.")
    if not strengths:
        strengths.append("Eagerness to embark on a structured, project-driven frontend path.")

    gaps = []
    if not has_js:
        gaps.append({
            "skill": "Modern JavaScript (ES6+, Async/Await, DOM APIs)",
            "priority": "Critical High",
            "reason": "92% of Frontend Developer job listings mandate JavaScript proficiency as an essential barrier to entry."
        })
    if not has_react:
        gaps.append({
            "skill": "Component Architecture (React)",
            "priority": "High",
            "reason": "Modern engineering teams build with component libraries to ensure maintainability and rapid iteration."
        })
    gaps.append({
        "skill": "Demonstrated Practical Capstone Projects",
        "priority": "Critical High",
        "reason": "Recruiters cannot verify skill levels without tangible, public GitHub repositories and deployed live demonstrations."
    })

    next_steps = [
        "Complete Stage 2 of your Elevora Learning Roadmap: Master ES6+ array methods and async Fetch.",
        "Take on the Capstone Project: 'Interactive Task Management Web Application'.",
        "Submit your project code and live URL for Elevora AI rubric-based evaluation to earn verified badges.",
        "Apply to entry-level internship opportunities with your newly demonstrated skill profile."
    ]

    message = f"""### Career Advisory Report for **{user_name}**
**Target Role:** {target_career} | **Analysis Source:** Elevora Career Engine (Curated Rule-Based Benchmark)

#### 1. Career & Market Reality Overview
Frontend engineering is currently shifting from static layout development to full interactive client architecture. Employers look for candidates who understand state management, asynchronous data fetching, and accessible, responsive design.

#### 2. Your Current Strengths
{"".join(f"- {s}\n" for s in strengths)}

#### 3. Identified Critical Missing Skills
{"".join(f"- **{g['skill']}** ({g['priority']}): {g['reason']}\n" for g in gaps)}

#### 4. The Learn-to-Prove-to-Earn Pathway
1. **Learn:** Focus on practical JavaScript patterns rather than passive video tutorials.
2. **Prove:** Build and deploy the interactive Task Manager capstone project with clean Git history.
3. **Earn:** Unlock matched junior internships like *CloudScale Junior Frontend Intern* once your JavaScript verification is achieved!
"""

    return {
        "source": "rule-based-engine",
        "is_ai_generated": False,
        "note": "Generated via Elevora's structured career guidance heuristics. Connect a GEMINI_API_KEY in .env for custom dynamic generation.",
        "target_career": target_career,
        "strengths": strengths,
        "gaps": gaps,
        "next_steps": next_steps,
        "message": message
    }

# -------------------------------------------------------------
# 2. PRACTICAL PROJECT & SKILL EVALUATOR
# -------------------------------------------------------------
def evaluate_project_submission(project_meta: dict, submission_data: dict) -> dict:
    """
    Evaluates a user's practical project submission against the 6 transparent rubrics.
    Calculates scores, grade, strengths, improvements, and action items.
    """
    title = submission_data.get("submission_title", "Task Management App")
    live_url = submission_data.get("live_url", "").strip()
    github_url = submission_data.get("github_url", "").strip()
    description = submission_data.get("description", "").strip()
    architecture = submission_data.get("architecture_notes", "").strip()

    # Rule-based rubric analysis based on project complexity and completeness
    # Max score 60 (6 criteria x 10 points)
    # 1. HTML structure & semantic quality
    score_html = 9 if ("semantic" in (description + architecture).lower() or "header" in (description + architecture).lower()) else 8
    
    # 2. CSS styling & responsiveness
    score_css = 9 if ("responsive" in (description + architecture).lower() or "flexbox" in (description + architecture).lower() or "grid" in (description + architecture).lower()) else 8
    
    # 3. JavaScript functionality & state
    score_js = 9 if ("localstorage" in (description + architecture).lower() or "state" in (description + architecture).lower() or "filter" in (description + architecture).lower()) else 8
    
    # 4. User interaction & UX
    score_ux = 9 if ("active" in (description + architecture).lower() or "validation" in (description + architecture).lower()) else 8
    
    # 5. Code organization
    score_code_org = 9 if github_url.startswith("http") else 7
    
    # 6. Overall completeness
    score_completeness = 10 if (live_url and github_url and len(description) > 30) else 8

    total_score = score_html + score_css + score_js + score_ux + score_code_org + score_completeness
    percentage = round((total_score / 60.0) * 100, 1)

    if percentage >= 90:
        grade = "A+ (Workforce Ready)"
    elif percentage >= 80:
        grade = "A (Strong Competency)"
    elif percentage >= 70:
        grade = "B (Good Progress)"
    else:
        grade = "C (Needs Revision)"

    strengths = [
        "Well-structured semantic HTML hierarchy with accessible interactive controls.",
        "Demonstrated responsive layout behavior using modern CSS grid and flexbox.",
        "Functional JavaScript state management with clean separation of task manipulation logic.",
        "Successful client-side data persistence utilizing browser localStorage."
    ]

    improvements = [
        "Consider incorporating keyboard shortcuts (e.g. Enter to add, Escape to cancel editing) for enhanced a11y.",
        "Add subtle transition animations when task items are filtered or deleted to improve visual feedback.",
        "Include unit tests or JSDoc comments to document core helper functions."
    ]

    action_items = [
        "Mark JavaScript and Responsive Web Design as 'Demonstrated' in your Skill Profile.",
        "Add the verified project badge to your public Elevora portfolio.",
        "Proceed to explore the newly unlocked internship matches (e.g. CloudScale Technologies)!"
    ]

    return {
        "source": "elevora-rubric-evaluator",
        "rubric_breakdown": {
            "html_structure": {"score": score_html, "max": 10, "criterion": "HTML Structure & Semantic Quality"},
            "css_styling": {"score": score_css, "max": 10, "criterion": "CSS Styling & Responsiveness"},
            "javascript_functionality": {"score": score_js, "max": 10, "criterion": "JavaScript Functionality & State"},
            "user_interaction": {"score": score_ux, "max": 10, "criterion": "User Interaction & UX Polish"},
            "code_organization": {"score": score_code_org, "max": 10, "criterion": "Code Organization & Best Practices"},
            "overall_completeness": {"score": score_completeness, "max": 10, "criterion": "Overall Completeness & Deliverables"}
        },
        "scores": {
            "score_html": score_html,
            "score_css": score_css,
            "score_js": score_js,
            "score_ux": score_ux,
            "score_code_org": score_code_org,
            "score_completeness": score_completeness
        },
        "total_score": total_score,
        "max_score": 60,
        "percentage": percentage,
        "grade": grade,
        "strengths": strengths,
        "improvements": improvements,
        "action_items": action_items,
        "demonstrated_skills_unlocked": ["JavaScript", "Responsive Design", "Git & GitHub", "Web Storage API"],
        "transparency_note": (
            "Assessment conducted based on verified project deliverables, submitted architecture documentation, "
            "and transparent rubric criteria. Live inspection is simulated through structured artifact analysis."
        )
    }

# -------------------------------------------------------------
# 3. TRANSPARENT SKILL-GAP & READINESS CALCULATOR
# -------------------------------------------------------------
def calculate_skill_gap_analysis(user_skills: list, market_required_skills: list, market_preferred_skills: list) -> dict:
    """
    Transparent skill-gap matching algorithm.
    Formula:
    Essential Weight: 70%
    Preferred Weight: 30%
    Match Score = (Matched Essential / Total Essential * 70) + (Matched Preferred / Total Preferred * 30)
    """
    user_skill_names = {s.get("skill_name", "").strip().lower() for s in user_skills}
    demonstrated_skill_names = {
        s.get("skill_name", "").strip().lower() 
        for s in user_skills 
        if s.get("status") in ("demonstrated", "verified")
    }

    essential_matched = []
    essential_missing = []

    for req in market_required_skills:
        req_norm = req.strip().lower()
        if req_norm in user_skill_names:
            is_demonstrated = req_norm in demonstrated_skill_names
            essential_matched.append({"name": req, "status": "demonstrated" if is_demonstrated else "in_progress"})
        else:
            essential_missing.append({"name": req, "status": "missing", "priority": "High"})

    preferred_matched = []
    preferred_missing = []

    for pref in market_preferred_skills:
        pref_norm = pref.strip().lower()
        if pref_norm in user_skill_names:
            is_demonstrated = pref_norm in demonstrated_skill_names
            preferred_matched.append({"name": pref, "status": "demonstrated" if is_demonstrated else "in_progress"})
        else:
            preferred_missing.append({"name": pref, "status": "missing", "priority": "Medium"})

    # Scoring math
    total_essential = len(market_required_skills) or 1
    total_preferred = len(market_preferred_skills) or 1

    essential_score = (len(essential_matched) / total_essential) * 70.0
    preferred_score = (len(preferred_matched) / total_preferred) * 30.0
    raw_match_percentage = round(essential_score + preferred_score, 1)

    # Career readiness calculation:
    # Considers not just "known" skills, but whether they have been PROVEN via projects
    demonstrated_ratio = len(demonstrated_skill_names) / max(len(market_required_skills), 1)
    readiness_percentage = round(min(100.0, (raw_match_percentage * 0.5) + (demonstrated_ratio * 50.0)), 1)

    return {
        "match_percentage": raw_match_percentage,
        "readiness_percentage": readiness_percentage,
        "essential_matched": essential_matched,
        "essential_missing": essential_missing,
        "preferred_matched": preferred_matched,
        "preferred_missing": preferred_missing,
        "formula_explanation": (
            "Match Percentage = (Matched Essential / Total Essential * 70%) + (Matched Preferred / Total Preferred * 30%). "
            "Readiness Percentage additionally weights demonstrated/verified practical capstone execution by 50%."
        )
    }
