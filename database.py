"""
ELEVORA AI - Database Layer
SQLite-backed persistence layer with transparent schema and realistic hackathon seed data.
"""

import sqlite3
import json
import hashlib
import os
import tempfile
from datetime import datetime
from pathlib import Path

def resolve_db_path():
    """Returns a reliable writable path for SQLite across all operating systems and environments."""
    # First try the workspace directory
    candidate = Path(__file__).resolve().parent / "elevora.db"
    try:
        test_conn = sqlite3.connect(str(candidate))
        test_conn.execute("CREATE TABLE IF NOT EXISTS _test_probe (id INT)")
        test_conn.close()
        return str(candidate)
    except Exception:
        # If OneDrive or OS file locking restricts direct local file creation, use system temp dir
        temp_candidate = os.path.join(tempfile.gettempdir(), "elevora_ai.db")
        return temp_candidate

DB_PATH = resolve_db_path()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db(force_reset=False):
    """Initializes tables and seeds default data."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if force_reset:
        cursor.executescript("""
            DROP TABLE IF EXISTS user_applications;
            DROP TABLE IF EXISTS user_project_submissions;
            DROP TABLE IF EXISTS user_roadmap_progress;
            DROP TABLE IF EXISTS user_skills;
            DROP TABLE IF EXISTS job_listings;
            DROP TABLE IF EXISTS learning_roadmap;
            DROP TABLE IF EXISTS projects;
            DROP TABLE IF EXISTS users;
        """)

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            education_level TEXT,
            academic_status TEXT,
            target_career TEXT DEFAULT 'Frontend Developer',
            experience_level TEXT DEFAULT 'Beginner',
            weekly_hours INTEGER DEFAULT 12,
            learning_style TEXT DEFAULT 'Practical Projects & Code Demos',
            onboarding_completed INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS user_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            level TEXT DEFAULT 'beginner',
            status TEXT DEFAULT 'in_progress',
            source TEXT DEFAULT 'onboarding',
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS learning_roadmap (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stage_id INTEGER NOT NULL,
            stage_title TEXT NOT NULL,
            lesson_id TEXT UNIQUE NOT NULL,
            skill_name TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            estimated_hours INTEGER NOT NULL,
            priority TEXT NOT NULL,
            resources_json TEXT NOT NULL,
            practice_activity TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS user_roadmap_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lesson_id TEXT NOT NULL,
            is_completed INTEGER DEFAULT 0,
            completed_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, lesson_id)
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            career_track TEXT NOT NULL,
            overview TEXT NOT NULL,
            objectives_json TEXT NOT NULL,
            required_tech_json TEXT NOT NULL,
            milestones_json TEXT NOT NULL,
            rubric_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS user_project_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            submission_title TEXT NOT NULL,
            live_url TEXT NOT NULL,
            github_url TEXT NOT NULL,
            description TEXT NOT NULL,
            architecture_notes TEXT,
            score_html INTEGER DEFAULT 0,
            score_css INTEGER DEFAULT 0,
            score_js INTEGER DEFAULT 0,
            score_ux INTEGER DEFAULT 0,
            score_code_org INTEGER DEFAULT 0,
            score_completeness INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0,
            percentage REAL DEFAULT 0.0,
            grade TEXT DEFAULT 'Pending',
            feedback_strengths_json TEXT,
            feedback_improvements_json TEXT,
            feedback_action_items_json TEXT,
            status TEXT DEFAULT 'evaluated',
            submitted_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS job_listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            opportunity_type TEXT NOT NULL,
            location TEXT NOT NULL,
            remote_status TEXT NOT NULL,
            experience_level TEXT NOT NULL,
            stipend_salary TEXT NOT NULL,
            description TEXT NOT NULL,
            required_skills_json TEXT NOT NULL,
            preferred_skills_json TEXT NOT NULL,
            application_url TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS user_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            status TEXT DEFAULT 'Applied',
            applied_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (job_id) REFERENCES job_listings(id) ON DELETE CASCADE,
            UNIQUE(user_id, job_id)
        );
    """)

    conn.commit()

    # Seed data if tables are empty
    seed_roadmap_data(conn)
    seed_project_data(conn)
    seed_job_listings_data(conn)
    seed_demo_user(conn)

    conn.close()

def seed_roadmap_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM learning_roadmap")
    if cursor.fetchone()[0] > 0:
        return

    stages = [
        # Stage 1: Strengthen Fundamentals
        {
            "stage_id": 1,
            "stage_title": "Stage 1: Strengthen Fundamentals",
            "lesson_id": "fund-101",
            "skill_name": "HTML5",
            "title": "Modern Semantic HTML & Accessibility (a11y)",
            "description": "Master clean document outlines, ARIA attributes, semantic tags (main, nav, article), and accessible forms.",
            "estimated_hours": 4,
            "priority": "Essential",
            "resources": [
                {"title": "MDN: HTML Semantic Elements", "url": "https://developer.mozilla.org/en-US/docs/Glossary/Semantics#semantics_in_html"},
                {"title": "freeCodeCamp: Responsive Web Design", "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/"}
            ],
            "practice_activity": "Refactor a div-soup landing page into a clean, keyboard-navigable semantic document structure."
        },
        {
            "stage_id": 1,
            "stage_title": "Stage 1: Strengthen Fundamentals",
            "lesson_id": "fund-102",
            "skill_name": "CSS3",
            "title": "Modern CSS Layouts: Flexbox, Grid & Responsive Tokens",
            "description": "Build production layouts without frameworks using CSS Flexbox, Grid, container queries, and mobile-first media queries.",
            "estimated_hours": 6,
            "priority": "Essential",
            "resources": [
                {"title": "MDN: CSS Grid Layout Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout"},
                {"title": "CSS-Tricks: Complete Guide to Flexbox", "url": "https://css-tricks.com/snippets/css/a-guide-to-flexbox/"}
            ],
            "practice_activity": "Create a fully responsive dashboard card grid that adapts seamlessly across mobile, tablet, and widescreen viewports."
        },

        # Stage 2: Master JavaScript
        {
            "stage_id": 2,
            "stage_title": "Stage 2: Master JavaScript",
            "lesson_id": "js-201",
            "skill_name": "JavaScript",
            "title": "Modern JavaScript ES6+ & Data Structures",
            "description": "Deep dive into array methods (map, filter, reduce), destructuring, closures, spread/rest syntax, and ES modules.",
            "estimated_hours": 8,
            "priority": "Essential",
            "resources": [
                {"title": "JavaScript.info: The Modern JavaScript Tutorial", "url": "https://javascript.info/"},
                {"title": "MDN: JavaScript Language Overview", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/A_re-introduction_to_JavaScript"}
            ],
            "practice_activity": "Implement a client-side filter and sorting algorithm for tabular job and skill records."
        },
        {
            "stage_id": 2,
            "stage_title": "Stage 2: Master JavaScript",
            "lesson_id": "js-202",
            "skill_name": "JavaScript",
            "title": "DOM Manipulation, Event Architecture & LocalStorage",
            "description": "Learn event delegation, dynamic DOM rendering, custom events, and persistent browser storage APIs.",
            "estimated_hours": 7,
            "priority": "Essential",
            "resources": [
                {"title": "MDN: Introduction to the DOM", "url": "https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction"},
                {"title": "MDN: Window.localStorage", "url": "https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage"}
            ],
            "practice_activity": "Build an interactive task list where tasks can be added, toggled, and persisted across browser reloads."
        },

        # Stage 3: Version Control & Git
        {
            "stage_id": 3,
            "stage_title": "Stage 3: Version Control & Git",
            "lesson_id": "git-301",
            "skill_name": "Git & GitHub",
            "title": "Professional Git Workflow, Branching & GitHub PRs",
            "description": "Essential version control commands, atomic commits, feature branches, resolving merge conflicts, and writing clean pull request descriptions.",
            "estimated_hours": 5,
            "priority": "Essential",
            "resources": [
                {"title": "GitHub Docs: Git Cheat Sheet", "url": "https://docs.github.com/en/get-started/quickstart/git-and-github-learning-resources"},
                {"title": "Atlassian Git Tutorial", "url": "https://www.atlassian.com/git/tutorials"}
            ],
            "practice_activity": "Initialize a repository, create a feature branch, resolve a staged merge conflict, and submit a documented pull request."
        },

        # Stage 4: Component-Based Architecture with React
        {
            "stage_id": 4,
            "stage_title": "Stage 4: Learn React",
            "lesson_id": "react-401",
            "skill_name": "React",
            "title": "React Core: JSX, Components, Props & State",
            "description": "Understand declarative UI programming, unidirectional data flow, component decomposition, and useState fundamentals.",
            "estimated_hours": 10,
            "priority": "Essential",
            "resources": [
                {"title": "Official React Documentation (react.dev)", "url": "https://react.dev/learn"},
                {"title": "freeCodeCamp: React for Beginners", "url": "https://www.freecodecamp.org/news/tag/react/"}
            ],
            "practice_activity": "Break down an interactive dashboard widget into isolated, reusable presentational and container components."
        },
        {
            "stage_id": 4,
            "stage_title": "Stage 4: Learn React",
            "lesson_id": "react-402",
            "skill_name": "React",
            "title": "Hooks Deep Dive: useEffect, Custom Hooks & Performance",
            "description": "Manage component side-effects, API calls, event listeners cleanup, memoization, and extracting business logic into custom hooks.",
            "estimated_hours": 8,
            "priority": "Essential",
            "resources": [
                {"title": "React Docs: Synchronizing with Effects", "url": "https://react.dev/learn/synchronizing-with-effects"},
                {"title": "React Docs: Reusing Logic with Custom Hooks", "url": "https://react.dev/learn/reusing-logic-with-custom-hooks"}
            ],
            "practice_activity": "Construct a custom `useLocalStorage` hook that synchronizes component state with browser storage."
        },

        # Stage 5: Real-World API Integration
        {
            "stage_id": 5,
            "stage_title": "Stage 5: API Integration & Practical Development",
            "lesson_id": "api-501",
            "skill_name": "API Integration",
            "title": "REST APIs, Fetch/Axios, Async/Await & Robust Error Handling",
            "description": "Master asynchronous client-server communication, JSON parsing, HTTP headers, loading states, error boundaries, and debounce strategies.",
            "estimated_hours": 7,
            "priority": "Essential",
            "resources": [
                {"title": "MDN: Using the Fetch API", "url": "https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch"},
                {"title": "REST API Tutorial", "url": "https://restfulapi.net/"}
            ],
            "practice_activity": "Implement a live search bar that queries an external public API with debounced user input and visual fallback states."
        }
    ]

    for item in stages:
        cursor.execute("""
            INSERT INTO learning_roadmap (
                stage_id, stage_title, lesson_id, skill_name, title, description,
                estimated_hours, priority, resources_json, practice_activity
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item["stage_id"], item["stage_title"], item["lesson_id"], item["skill_name"],
            item["title"], item["description"], item["estimated_hours"], item["priority"],
            json.dumps(item["resources"]), item["practice_activity"]
        ))
    conn.commit()

def seed_project_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM projects")
    if cursor.fetchone()[0] > 0:
        return

    project = {
        "slug": "task-management-app",
        "title": "Interactive Task Management Web Application",
        "career_track": "Frontend Developer",
        "overview": (
            "Build an interactive, responsive task management application (Kanban / Todo style). "
            "This capstone project requires you to apply HTML5 semantic structure, modern responsive CSS layouts, "
            "modular JavaScript logic, state persistence via LocalStorage, and clean interactive UX to prove "
            "your frontend readiness."
        ),
        "objectives": [
            "Demonstrate clean, semantic HTML5 structure and accessible form elements.",
            "Implement modern CSS Flexbox and Grid layouts responsive from mobile to desktop.",
            "Write modular JavaScript managing tasks state (create, toggle status, edit, delete).",
            "Implement task filtering by status (All, Active, Completed) and search query.",
            "Persist task data locally using Web Storage API (localStorage).",
            "Deliver clean code organization with documented Git commits."
        ],
        "required_tech": ["HTML5", "CSS3 / Responsive Design", "JavaScript (ES6+)", "Git & GitHub", "Web Storage API"],
        "milestones": [
            {"id": "m1", "title": "Milestone 1: Semantic Document Architecture & Accessibility", "desc": "Setup semantic tags, accessible forms, aria-labels, and base HTML structure."},
            {"id": "m2", "title": "Milestone 2: Responsive Visual Styling & Layouts", "desc": "Design a clean desktop & mobile UI using CSS Flexbox/Grid with modern styling."},
            {"id": "m3", "title": "Milestone 3: Dynamic State & DOM Manipulation", "desc": "Write JS functions to render tasks, handle additions, status toggling, and deletions."},
            {"id": "m4", "title": "Milestone 4: Storage Persistence & Search/Filter Controls", "desc": "Add LocalStorage sync and filter controls (All, In Progress, Completed)."}
        ],
        "rubric": [
            {"criterion": "HTML Structure & Semantic Quality", "weight": 10, "desc": "Proper use of header, main, section, nav, form tags, and accessible input labeling."},
            {"criterion": "CSS Styling & Responsiveness", "weight": 10, "desc": "Fluid mobile-to-desktop layout, readable typography, contrast adherence, and clean transitions."},
            {"criterion": "JavaScript Functionality & State", "weight": 10, "desc": "Correct state updates, immutable data patterns, event listeners, and filtering logic."},
            {"criterion": "User Interaction & UX Polish", "weight": 10, "desc": "Clear active states, form validation, confirmation toasts, and intuitive task actions."},
            {"criterion": "Code Organization & Best Practices", "weight": 10, "desc": "Modular functions, clean variable naming, separation of concerns, and meaningful Git commits."},
            {"criterion": "Overall Completeness & Polish", "weight": 10, "desc": "All requirements satisfied, zero console bugs, and thoughtful attention to detail."}
        ]
    }

    cursor.execute("""
        INSERT INTO projects (
            slug, title, career_track, overview, objectives_json, required_tech_json, milestones_json, rubric_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        project["slug"], project["title"], project["career_track"], project["overview"],
        json.dumps(project["objectives"]), json.dumps(project["required_tech"]),
        json.dumps(project["milestones"]), json.dumps(project["rubric"])
    ))
    conn.commit()

def seed_job_listings_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM job_listings")
    if cursor.fetchone()[0] > 0:
        return

    sample_jobs = [
        {
            "slug": "cloudscale-junior-frontend-intern",
            "title": "Junior Frontend Developer Intern",
            "company": "CloudScale Technologies",
            "opportunity_type": "Internship",
            "location": "San Francisco, CA",
            "remote_status": "Remote",
            "experience_level": "Entry-Level / Student",
            "stipend_salary": "$30 - $38 / hr",
            "description": (
                "CloudScale is seeking a passionate Frontend Intern to join our web app team. "
                "You will collaborate on building modern user interfaces, integrating RESTful APIs, "
                "and turning design prototypes into accessible web components."
            ),
            "required_skills": ["HTML5", "CSS3", "JavaScript", "Git & GitHub", "Responsive Design"],
            "preferred_skills": ["React", "API Integration", "TypeScript"],
            "application_url": "https://careers.cloudscale-sample.io/jobs/frontend-intern"
        },
        {
            "slug": "novatech-ui-engineering-fellow",
            "title": "Associate UI Engineer",
            "company": "NovaTech Labs",
            "opportunity_type": "Entry-Level Junior",
            "location": "New York, NY",
            "remote_status": "Hybrid",
            "experience_level": "0-1 Years Experience",
            "stipend_salary": "$70,000 - $85,000 / yr",
            "description": (
                "Work directly with product designers and backend engineers to develop rich, responsive web applications. "
                "Candidates must possess demonstrated competence in JavaScript, CSS Grid/Flexbox, and component architecture."
            ),
            "required_skills": ["HTML5", "CSS3", "JavaScript", "React", "Git & GitHub"],
            "preferred_skills": ["API Integration", "Tailwind CSS", "Unit Testing"],
            "application_url": "https://novatech-sample.dev/careers/associate-ui"
        },
        {
            "slug": "apexdigital-web-developer-trainee",
            "title": "Junior Web Developer",
            "company": "Apex Digital Studio",
            "opportunity_type": "Entry-Level Junior",
            "location": "Austin, TX",
            "remote_status": "Remote",
            "experience_level": "Entry-Level",
            "stipend_salary": "$65,000 - $78,000 / yr",
            "description": (
                "Apex Digital crafts high-performance web products for fast-growing companies. "
                "We welcome graduates with strong fundamentals in semantic HTML, modern responsive CSS, and DOM programming."
            ),
            "required_skills": ["HTML5", "CSS3", "JavaScript", "Responsive Design", "Git & GitHub"],
            "preferred_skills": ["React", "Performance Optimization"],
            "application_url": "https://apexdigital-sample.com/apply/jr-web"
        },
        {
            "slug": "finpulse-frontend-fellow",
            "title": "Frontend Engineering Apprentice",
            "company": "FinPulse Solutions",
            "opportunity_type": "Internship",
            "location": "Boston, MA",
            "remote_status": "On-Site",
            "experience_level": "Undergraduate / Graduate",
            "stipend_salary": "$28 - $34 / hr",
            "description": (
                "Join FinPulse's 6-month apprentice program. You'll gain hands-on experience building financial analytics "
                "dashboards, working with REST APIs, and writing maintainable frontend code."
            ),
            "required_skills": ["HTML5", "CSS3", "JavaScript", "Git & GitHub"],
            "preferred_skills": ["React", "API Integration", "Chart.js"],
            "application_url": "https://finpulse-sample.org/fellowship"
        },
        {
            "slug": "eduvibe-frontend-apprentice",
            "title": "Junior React & Web Developer",
            "company": "EduVibe Interactive",
            "opportunity_type": "Entry-Level Junior",
            "location": "Seattle, WA",
            "remote_status": "Remote",
            "experience_level": "0-2 Years",
            "stipend_salary": "$72,000 - $88,000 / yr",
            "description": (
                "EduVibe builds interactive learning tools for higher education. We value candidates who have built practical "
                "projects, demonstrated clean code organization, and understand modern state management."
            ),
            "required_skills": ["HTML5", "CSS3", "JavaScript", "React", "API Integration"],
            "preferred_skills": ["Git & GitHub", "TypeScript", "Accessibility"],
            "application_url": "https://eduvibe-sample.tech/jobs/react-dev"
        }
    ]

    for job in sample_jobs:
        cursor.execute("""
            INSERT INTO job_listings (
                slug, title, company, opportunity_type, location, remote_status,
                experience_level, stipend_salary, description, required_skills_json,
                preferred_skills_json, application_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job["slug"], job["title"], job["company"], job["opportunity_type"], job["location"],
            job["remote_status"], job["experience_level"], job["stipend_salary"], job["description"],
            json.dumps(job["required_skills"]), json.dumps(job["preferred_skills"]), job["application_url"]
        ))
    conn.commit()

def seed_demo_user(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = 'demo@elevora.ai'")
    existing = cursor.fetchone()
    if existing:
        return existing[0]

    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO users (
            email, password_hash, full_name, education_level, academic_status,
            target_career, experience_level, weekly_hours, learning_style, onboarding_completed, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "demo@elevora.ai",
        hash_password("elevora2026"),
        "Alex Chen",
        "Bachelor of Science (CSE, 3rd Year)",
        "Undergraduate Student",
        "Frontend Developer",
        "Beginner / Intermediate",
        14,
        "Practical Projects & Code Demos",
        1,
        now
    ))
    user_id = cursor.lastrowid

    # Initial Skills for Demo Student:
    # Knows HTML and CSS well; has limited JavaScript; lacks Git & React & practical project portfolio
    initial_skills = [
        ("HTML5", "intermediate", "demonstrated", "onboarding"),
        ("CSS3", "intermediate", "demonstrated", "onboarding"),
        ("Responsive Design", "intermediate", "demonstrated", "onboarding"),
        ("JavaScript", "beginner", "in_progress", "onboarding"),
        ("Git & GitHub", "beginner", "in_progress", "onboarding")
    ]
    for skill, level, status, source in initial_skills:
        cursor.execute("""
            INSERT INTO user_skills (user_id, skill_name, level, status, source, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, skill, level, status, source, now))

    # Mark Stage 1 lessons completed initially (Fundamentals)
    cursor.execute("""
        INSERT INTO user_roadmap_progress (user_id, lesson_id, is_completed, completed_at)
        VALUES (?, 'fund-101', 1, ?), (?, 'fund-102', 1, ?)
    """, (user_id, now, user_id, now))

    conn.commit()
    return user_id

def reset_demo_user():
    """Resets the demo user to the canonical initial state for the Hackathon Demonstration scenario."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = 'demo@elevora.ai'")
    user = cursor.fetchone()

    if user:
        user_id = user["id"]
        # Clear submissions, progress, applications, skills
        cursor.execute("DELETE FROM user_project_submissions WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM user_roadmap_progress WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM user_applications WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM user_skills WHERE user_id = ?", (user_id,))

        now = datetime.now().isoformat()
        # Reset user metadata
        cursor.execute("""
            UPDATE users SET
                full_name = 'Alex Chen',
                education_level = 'Bachelor of Science (CSE, 3rd Year)',
                academic_status = 'Undergraduate Student',
                target_career = 'Frontend Developer',
                experience_level = 'Beginner / Intermediate',
                weekly_hours = 14,
                onboarding_completed = 1
            WHERE id = ?
        """, (user_id,))

        # Initial skills
        initial_skills = [
            ("HTML5", "intermediate", "demonstrated", "onboarding"),
            ("CSS3", "intermediate", "demonstrated", "onboarding"),
            ("Responsive Design", "intermediate", "demonstrated", "onboarding"),
            ("JavaScript", "beginner", "in_progress", "onboarding"),
            ("Git & GitHub", "beginner", "in_progress", "onboarding")
        ]
        for skill, level, status, source in initial_skills:
            cursor.execute("""
                INSERT INTO user_skills (user_id, skill_name, level, status, source, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, skill, level, status, source, now))

        # Initial progress (Fundamentals done, JS/React/Git pending)
        cursor.execute("""
            INSERT INTO user_roadmap_progress (user_id, lesson_id, is_completed, completed_at)
            VALUES (?, 'fund-101', 1, ?), (?, 'fund-102', 1, ?)
        """, (user_id, now, user_id, now))

        conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db(force_reset=True)
    print("Database initialized successfully at:", DB_PATH)
