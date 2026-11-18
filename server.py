"""
ELEVORA AI - Backend REST API & Web Server
A robust, high-performance HTTP & REST server using Python's standard library.
Requires zero external pip dependencies and runs instantly on Python 3.
"""

import sys
import os
import json
import sqlite3
import mimetypes
from datetime import datetime
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import database
import ai_service

PORT = int(os.environ.get("PORT", 8000))
HOST = os.environ.get("HOST", "0.0.0.0")
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

class ElevoraRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Clean server log format
        sys.stderr.write(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]} {args[1]} -> {args[2]}\n")

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def send_json(self, data, status=200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def parse_json_body(self):
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len == 0:
            return {}
        try:
            raw = self.rfile.read(content_len).decode("utf-8")
            return json.loads(raw)
        except Exception:
            return {}

    def get_auth_user_id(self):
        """Extracts user ID from Authorization header or defaults to Demo User (ID 1)."""
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:].strip()
            if token.isdigit():
                return int(token)
        # Default to demo user
        return 1

    # -----------------------------------------------------------------
    # ROUTER
    # -----------------------------------------------------------------
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path.startswith("/api/"):
            self.handle_api_get(path, parse_qs(parsed.query))
        else:
            self.serve_static_file(parsed.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path.startswith("/api/"):
            self.handle_api_post(path)
        else:
            self.send_json({"error": "Not Found"}, status=404)

    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path.startswith("/api/"):
            self.handle_api_put(path)
        else:
            self.send_json({"error": "Not Found"}, status=404)

    # -----------------------------------------------------------------
    # API HANDLERS - GET
    # -----------------------------------------------------------------
    def handle_api_get(self, path, query_params):
        user_id = self.get_auth_user_id()
        conn = database.get_db_connection()

        try:
            if path == "/api/profile":
                self.api_get_profile(conn, user_id)
            elif path == "/api/market/jobs":
                self.api_get_market_jobs(conn, user_id)
            elif path == "/api/skills/gap-analysis":
                self.api_get_gap_analysis(conn, user_id)
            elif path == "/api/roadmap":
                self.api_get_roadmap(conn, user_id)
            elif path == "/api/projects":
                self.api_get_projects(conn, user_id)
            elif path == "/api/portfolio":
                self.api_get_portfolio(conn, user_id)
            elif path == "/api/opportunities":
                self.api_get_opportunities(conn, user_id)
            elif path == "/api/health":
                self.send_json({"status": "healthy", "service": "elevora-ai-backend", "time": datetime.now().isoformat()})
            else:
                self.send_json({"error": f"Endpoint not found: {path}"}, status=404)
        finally:
            conn.close()

    def api_get_profile(self, conn, user_id):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        if not user_row:
            # Fallback to first user
            cursor.execute("SELECT * FROM users LIMIT 1")
            user_row = cursor.fetchone()

        if not user_row:
            self.send_json({"error": "User not found"}, status=404)
            return

        user_data = dict(user_row)
        user_data.pop("password_hash", None)

        # Get skills
        cursor.execute("SELECT * FROM user_skills WHERE user_id = ?", (user_data["id"],))
        skills = [dict(r) for r in cursor.fetchall()]
        user_data["skills"] = skills

        # Calculate live readiness
        readiness = self.calculate_user_readiness(conn, user_data["id"])
        user_data["readiness"] = readiness

        self.send_json({"success": True, "user": user_data})

    def calculate_user_readiness(self, conn, user_id):
        cursor = conn.cursor()
        # Market benchmark skills for Frontend Developer
        market_essential = ["HTML5", "CSS3", "JavaScript", "Responsive Design", "Git & GitHub"]
        market_preferred = ["React", "API Integration", "Web Storage API"]

        cursor.execute("SELECT skill_name, status FROM user_skills WHERE user_id = ?", (user_id,))
        skills = [dict(r) for r in cursor.fetchall()]

        gap = ai_service.calculate_skill_gap_analysis(skills, market_essential, market_preferred)

        # Project completion status
        cursor.execute("SELECT COUNT(*) FROM user_project_submissions WHERE user_id = ? AND percentage >= 70", (user_id,))
        projects_completed = cursor.fetchone()[0]

        # Roadmap progress
        cursor.execute("SELECT COUNT(*) FROM user_roadmap_progress WHERE user_id = ? AND is_completed = 1", (user_id,))
        lessons_completed = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM learning_roadmap")
        total_lessons = cursor.fetchone()[0] or 1

        roadmap_pct = round((lessons_completed / total_lessons) * 100, 1)

        return {
            "overall_score": gap["readiness_percentage"],
            "skill_match_percentage": gap["match_percentage"],
            "lessons_completed": lessons_completed,
            "total_lessons": total_lessons,
            "roadmap_progress_percentage": roadmap_pct,
            "projects_completed": projects_completed,
            "stage": "PROVE" if (projects_completed > 0 or roadmap_pct >= 60) else "LEARN"
        }

    def api_get_market_jobs(self, conn, user_id):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM job_listings")
        rows = cursor.fetchall()

        jobs = []
        skill_counts = {}
        total_postings = len(rows)

        for r in rows:
            job = dict(r)
            req = json.loads(job["required_skills_json"])
            pref = json.loads(job["preferred_skills_json"])
            job["required_skills"] = req
            job["preferred_skills"] = pref

            for s in req:
                skill_counts[s] = skill_counts.get(s, 0) + 1
            jobs.append(job)

        # Market skill demand breakdown
        demand_stats = []
        for skill, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True):
            demand_stats.append({
                "skill": skill,
                "frequency": count,
                "demand_percentage": round((count / max(total_postings, 1)) * 100, 1)
            })

        self.send_json({
            "success": True,
            "total_listings_analyzed": total_postings,
            "target_role": "Frontend Developer",
            "market_demand_statistics": demand_stats,
            "sample_listings": jobs,
            "disclaimer": "Curated benchmark dataset of 5 real-world industry job descriptions for academic hackathon analysis."
        })

    def api_get_gap_analysis(self, conn, user_id):
        cursor = conn.cursor()
        cursor.execute("SELECT skill_name, status, level FROM user_skills WHERE user_id = ?", (user_id,))
        user_skills = [dict(r) for r in cursor.fetchall()]

        market_essential = ["HTML5", "CSS3", "JavaScript", "Responsive Design", "Git & GitHub"]
        market_preferred = ["React", "API Integration", "Web Storage API"]

        analysis = ai_service.calculate_skill_gap_analysis(user_skills, market_essential, market_preferred)

        # Detail cards for gaps
        gap_details = []
        for m in analysis["essential_missing"]:
            reasons = {
                "JavaScript": "Required by 92% of frontend job listings for interactive DOM manipulation and asynchronous state.",
                "Git & GitHub": "Standard industry workflow for team version control, pull requests, and continuous integration.",
                "Responsive Design": "Mandatory standard ensuring web apps provide accessible viewports on all device sizes."
            }
            gap_details.append({
                "skill": m["name"],
                "category": "Essential",
                "priority": "Critical High",
                "reason": reasons.get(m["name"], "Core employer requirement for entry-level candidates."),
                "recommended_stage": "Stage 2 or 3 in Elevora Roadmap",
                "est_hours": 8
            })

        for m in analysis["preferred_missing"]:
            gap_details.append({
                "skill": m["name"],
                "category": "Preferred",
                "priority": "Medium",
                "reason": "Significantly differentiates candidate applications and unlocks higher salary bands.",
                "recommended_stage": "Stage 4 in Elevora Roadmap",
                "est_hours": 10
            })

        self.send_json({
            "success": True,
            "target_career": "Frontend Developer",
            "analysis": analysis,
            "gap_details": gap_details,
            "user_skills_count": len(user_skills)
        })

    def api_get_roadmap(self, conn, user_id):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM learning_roadmap ORDER BY stage_id, id")
        lessons_raw = cursor.fetchall()

        cursor.execute("SELECT lesson_id, is_completed, completed_at FROM user_roadmap_progress WHERE user_id = ?", (user_id,))
        progress_map = {r["lesson_id"]: bool(r["is_completed"]) for r in cursor.fetchall()}

        stages = {}
        for row in lessons_raw:
            lesson = dict(row)
            lesson["resources"] = json.loads(lesson["resources_json"])
            lesson["is_completed"] = progress_map.get(lesson["lesson_id"], False)

            stage_id = lesson["stage_id"]
            if stage_id not in stages:
                stages[stage_id] = {
                    "stage_id": stage_id,
                    "stage_title": lesson["stage_title"],
                    "lessons": []
                }
            stages[stage_id]["lessons"].append(lesson)

        self.send_json({
            "success": True,
            "stages": list(stages.values()),
            "total_lessons": len(lessons_raw),
            "completed_lessons": sum(1 for v in progress_map.values() if v)
        })

    def api_get_projects(self, conn, user_id):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects LIMIT 1")
        proj_row = cursor.fetchone()
        if not proj_row:
            self.send_json({"error": "No projects configured"}, status=404)
            return

        project = dict(proj_row)
        project["objectives"] = json.loads(project["objectives_json"])
        project["required_tech"] = json.loads(project["required_tech_json"])
        project["milestones"] = json.loads(project["milestones_json"])
        project["rubric"] = json.loads(project["rubric_json"])

        # Check existing submission for this user
        cursor.execute("SELECT * FROM user_project_submissions WHERE user_id = ? AND project_id = ? ORDER BY id DESC LIMIT 1", (user_id, project["id"]))
        sub_row = cursor.fetchone()
        submission = None
        if sub_row:
            submission = dict(sub_row)
            submission["feedback_strengths"] = json.loads(submission["feedback_strengths_json"] or "[]")
            submission["feedback_improvements"] = json.loads(submission["feedback_improvements_json"] or "[]")
            submission["feedback_action_items"] = json.loads(submission["feedback_action_items_json"] or "[]")

        self.send_json({
            "success": True,
            "project": project,
            "current_submission": submission
        })

    def api_get_portfolio(self, conn, user_id):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        if not user_row:
            self.send_json({"error": "User not found"}, status=404)
            return

        user_data = dict(user_row)
        user_data.pop("password_hash", None)

        cursor.execute("SELECT * FROM user_skills WHERE user_id = ?", (user_id,))
        skills = [dict(r) for r in cursor.fetchall()]

        # Categorize skills into the 3 tiers required:
        # 1. Learning in progress
        # 2. Demonstrated through projects
        # 3. Verified through platform rubric
        in_progress_skills = [s for s in skills if s["status"] == "in_progress"]
        demonstrated_skills = [s for s in skills if s["status"] == "demonstrated"]
        verified_skills = [s for s in skills if s["status"] == "verified"]

        cursor.execute("""
            SELECT s.*, p.title as project_title, p.overview as project_overview
            FROM user_project_submissions s
            JOIN projects p ON s.project_id = p.id
            WHERE s.user_id = ?
            ORDER BY s.id DESC
        """, (user_id,))
        submissions = []
        for r in cursor.fetchall():
            item = dict(r)
            item["feedback_strengths"] = json.loads(item["feedback_strengths_json"] or "[]")
            item["feedback_improvements"] = json.loads(item["feedback_improvements_json"] or "[]")
            submissions.append(item)

        self.send_json({
            "success": True,
            "user": user_data,
            "skills_tier": {
                "in_progress": in_progress_skills,
                "demonstrated": demonstrated_skills,
                "verified": verified_skills
            },
            "completed_projects": submissions
        })

    def api_get_opportunities(self, conn, user_id):
        cursor = conn.cursor()
        cursor.execute("SELECT skill_name, status FROM user_skills WHERE user_id = ?", (user_id,))
        user_skills = [dict(r) for r in cursor.fetchall()]
        user_skill_names = {s["skill_name"].lower() for s in user_skills}
        demonstrated_names = {s["skill_name"].lower() for s in user_skills if s["status"] in ("demonstrated", "verified")}

        cursor.execute("SELECT job_id, status FROM user_applications WHERE user_id = ?", (user_id,))
        applied_map = {r["job_id"]: r["status"] for r in cursor.fetchall()}

        cursor.execute("SELECT * FROM job_listings")
        rows = cursor.fetchall()
        opportunities = []

        for r in rows:
            job = dict(r)
            req = json.loads(job["required_skills_json"])
            pref = json.loads(job["preferred_skills_json"])

            matched_req = [s for s in req if s.lower() in user_skill_names]
            missing_req = [s for s in req if s.lower() not in user_skill_names]

            matched_pref = [s for s in pref if s.lower() in user_skill_names]
            missing_pref = [s for s in pref if s.lower() not in user_skill_names]

            # Calculate match percentage
            req_score = (len(matched_req) / max(len(req), 1)) * 75.0
            pref_score = (len(matched_pref) / max(len(pref), 1)) * 25.0
            match_pct = round(req_score + pref_score, 1)

            # Check if user has proven skills for this role
            proven_count = sum(1 for s in req if s.lower() in demonstrated_names)
            is_ready_to_apply = (match_pct >= 75.0) and (proven_count >= 2)

            explanation = ""
            if is_ready_to_apply:
                explanation = f"Strong match ({match_pct}%). You possess {len(matched_req)}/{len(req)} essential skills with verified project deliverables."
            else:
                missing_str = ", ".join(missing_req[:2])
                explanation = f"Moderate match ({match_pct}%). To become a competitive applicant, complete and verify: {missing_str}."

            job["required_skills"] = req
            job["preferred_skills"] = pref
            job["matched_skills"] = matched_req + matched_pref
            job["missing_skills"] = missing_req + missing_pref
            job["match_percentage"] = match_pct
            job["is_ready_to_apply"] = is_ready_to_apply
            job["explanation"] = explanation
            job["application_status"] = applied_map.get(job["id"], None)

            opportunities.append(job)

        # Sort by match percentage descending
        opportunities.sort(key=lambda x: x["match_percentage"], reverse=True)

        self.send_json({
            "success": True,
            "opportunities": opportunities,
            "disclaimer": "All listings are simulated educational benchmarks curated for hackathon demonstration."
        })

    # -----------------------------------------------------------------
    # API HANDLERS - POST & PUT
    # -----------------------------------------------------------------
    def handle_api_post(self, path):
        body = self.parse_json_body()
        conn = database.get_db_connection()

        try:
            if path == "/api/auth/demo":
                # Quick Demo Mode Login
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = 'demo@elevora.ai'")
                user = cursor.fetchone()
                if not user:
                    database.seed_demo_user(conn)
                    cursor.execute("SELECT * FROM users WHERE email = 'demo@elevora.ai'")
                    user = cursor.fetchone()

                user_data = dict(user)
                user_data.pop("password_hash", None)
                self.send_json({"success": True, "token": str(user_data["id"]), "user": user_data})

            elif path == "/api/auth/login":
                email = body.get("email", "").strip().lower()
                password = body.get("password", "").strip()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                user = cursor.fetchone()
                if user and user["password_hash"] == database.hash_password(password):
                    user_data = dict(user)
                    user_data.pop("password_hash", None)
                    self.send_json({"success": True, "token": str(user_data["id"]), "user": user_data})
                else:
                    self.send_json({"success": False, "error": "Invalid email or password"}, status=401)

            elif path == "/api/auth/register":
                email = body.get("email", "").strip().lower()
                password = body.get("password", "").strip()
                full_name = body.get("full_name", "").strip() or "Student"
                if not email or not password:
                    self.send_json({"success": False, "error": "Email and password are required"}, status=400)
                    return

                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        INSERT INTO users (email, password_hash, full_name, created_at, onboarding_completed)
                        VALUES (?, ?, ?, ?, 0)
                    """, (email, database.hash_password(password), full_name, datetime.now().isoformat()))
                    conn.commit()
                    user_id = cursor.lastrowid
                    self.send_json({"success": True, "token": str(user_id), "user": {"id": user_id, "email": email, "full_name": full_name, "onboarding_completed": 0}})
                except sqlite3.IntegrityError:
                    self.send_json({"success": False, "error": "Email is already registered"}, status=400)

            elif path == "/api/advisor/chat":
                query = body.get("query", "").strip()
                user_id = self.get_auth_user_id()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                user_row = cursor.fetchone()
                user_dict = dict(user_row) if user_row else {"full_name": "Student", "target_career": "Frontend Developer"}

                cursor.execute("SELECT * FROM user_skills WHERE user_id = ?", (user_id,))
                user_dict["skills"] = [dict(r) for r in cursor.fetchall()]

                response = ai_service.get_career_advice(query, user_dict)
                self.send_json({"success": True, "response": response})

            elif path == "/api/roadmap/toggle-lesson":
                user_id = self.get_auth_user_id()
                lesson_id = body.get("lesson_id")
                is_completed = 1 if body.get("is_completed") else 0
                now = datetime.now().isoformat()

                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_roadmap_progress (user_id, lesson_id, is_completed, completed_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id, lesson_id) DO UPDATE SET
                        is_completed = excluded.is_completed,
                        completed_at = excluded.completed_at
                """, (user_id, lesson_id, is_completed, now))

                # Check lesson skill name to also advance skill status
                cursor.execute("SELECT skill_name FROM learning_roadmap WHERE lesson_id = ?", (lesson_id,))
                row = cursor.fetchone()
                if row and is_completed:
                    skill_name = row[0]
                    cursor.execute("""
                        INSERT INTO user_skills (user_id, skill_name, level, status, source, updated_at)
                        VALUES (?, ?, 'intermediate', 'in_progress', 'roadmap', ?)
                        ON CONFLICT DO NOTHING
                    """, (user_id, skill_name, now))

                conn.commit()
                self.send_json({"success": True, "lesson_id": lesson_id, "is_completed": bool(is_completed)})

            elif path == "/api/projects/submit":
                user_id = self.get_auth_user_id()
                project_id = body.get("project_id", 1)
                sub_title = body.get("submission_title", "Interactive Task Management Web Application")
                live_url = body.get("live_url", "").strip()
                github_url = body.get("github_url", "").strip()
                description = body.get("description", "").strip()
                architecture = body.get("architecture_notes", "").strip()

                if not live_url or not github_url or not description:
                    self.send_json({"success": False, "error": "Live URL, GitHub URL, and description are required"}, status=400)
                    return

                # Perform rubric evaluation
                eval_res = ai_service.evaluate_project_submission({}, body)
                scores = eval_res["scores"]
                now = datetime.now().isoformat()

                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_project_submissions (
                        user_id, project_id, submission_title, live_url, github_url, description, architecture_notes,
                        score_html, score_css, score_js, score_ux, score_code_org, score_completeness,
                        total_score, percentage, grade, feedback_strengths_json, feedback_improvements_json,
                        feedback_action_items_json, status, submitted_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'evaluated', ?)
                """, (
                    user_id, project_id, sub_title, live_url, github_url, description, architecture,
                    scores["score_html"], scores["score_css"], scores["score_js"], scores["score_ux"],
                    scores["score_code_org"], scores["score_completeness"], eval_res["total_score"],
                    eval_res["percentage"], eval_res["grade"], json.dumps(eval_res["strengths"]),
                    json.dumps(eval_res["improvements"]), json.dumps(eval_res["action_items"]), now
                ))

                # Upgrade unlocked skills to "demonstrated" and "verified"
                for skill in eval_res["demonstrated_skills_unlocked"]:
                    cursor.execute("""
                        INSERT INTO user_skills (user_id, skill_name, level, status, source, updated_at)
                        VALUES (?, ?, 'intermediate', 'demonstrated', 'project_eval', ?)
                        ON CONFLICT DO NOTHING
                    """, (user_id, skill, now))
                    cursor.execute("""
                        UPDATE user_skills SET status = 'demonstrated', level = 'intermediate', updated_at = ?
                        WHERE user_id = ? AND skill_name = ?
                    """, (now, user_id, skill))

                conn.commit()
                self.send_json({"success": True, "evaluation": eval_res})

            elif path == "/api/opportunities/apply":
                user_id = self.get_auth_user_id()
                job_id = body.get("job_id")
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                cursor.execute("""
                    INSERT INTO user_applications (user_id, job_id, status, applied_at)
                    VALUES (?, ?, 'Applied', ?)
                    ON CONFLICT(user_id, job_id) DO UPDATE SET status = 'Applied', applied_at = excluded.applied_at
                """, (user_id, job_id, now))
                conn.commit()
                self.send_json({"success": True, "message": "Application submitted successfully!", "job_id": job_id})

            elif path == "/api/reset-demo":
                database.reset_demo_user()
                self.send_json({"success": True, "message": "Demo data reset successfully to Step 1 initial state!"})

            else:
                self.send_json({"error": f"Endpoint not found: {path}"}, status=404)
        finally:
            conn.close()

    def handle_api_put(self, path):
        body = self.parse_json_body()
        conn = database.get_db_connection()
        user_id = self.get_auth_user_id()

        try:
            if path == "/api/profile":
                cursor = conn.cursor()
                now = datetime.now().isoformat()

                full_name = body.get("full_name")
                target_career = body.get("target_career", "Frontend Developer")
                education_level = body.get("education_level")
                academic_status = body.get("academic_status")
                weekly_hours = body.get("weekly_hours", 12)
                experience_level = body.get("experience_level", "Beginner")

                cursor.execute("""
                    UPDATE users SET
                        full_name = COALESCE(?, full_name),
                        target_career = COALESCE(?, target_career),
                        education_level = COALESCE(?, education_level),
                        academic_status = COALESCE(?, academic_status),
                        weekly_hours = COALESCE(?, weekly_hours),
                        experience_level = COALESCE(?, experience_level),
                        onboarding_completed = 1
                    WHERE id = ?
                """, (full_name, target_career, education_level, academic_status, weekly_hours, experience_level, user_id))

                # Update skills if provided
                if "skills" in body and isinstance(body["skills"], list):
                    # Replace skills
                    cursor.execute("DELETE FROM user_skills WHERE user_id = ?", (user_id,))
                    for sk in body["skills"]:
                        s_name = sk.get("skill_name") if isinstance(sk, dict) else str(sk)
                        s_level = sk.get("level", "intermediate") if isinstance(sk, dict) else "intermediate"
                        s_status = sk.get("status", "in_progress") if isinstance(sk, dict) else "in_progress"
                        cursor.execute("""
                            INSERT INTO user_skills (user_id, skill_name, level, status, source, updated_at)
                            VALUES (?, ?, ?, ?, 'onboarding', ?)
                        """, (user_id, s_name, s_level, s_status, now))

                conn.commit()
                self.send_json({"success": True, "message": "Profile updated successfully"})
            else:
                self.send_json({"error": f"Endpoint not found: {path}"}, status=404)
        finally:
            conn.close()

    # -----------------------------------------------------------------
    # STATIC FILE SERVING WITH SPA FALLBACK
    # -----------------------------------------------------------------
    def serve_static_file(self, req_path):
        clean_path = req_path.lstrip("/")
        if not clean_path:
            clean_path = "index.html"

        file_path = (STATIC_DIR / clean_path).resolve()

        # Prevent directory traversal
        if not str(file_path).startswith(str(STATIC_DIR.resolve())):
            self.send_json({"error": "Forbidden"}, status=403)
            return

        # If file doesn't exist, SPA fallback to index.html
        if not file_path.exists() or file_path.is_dir():
            file_path = STATIC_DIR / "index.html"

        if not file_path.exists():
            self.send_json({"error": "Application static bundle not found"}, status=404)
            return

        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = "application/octet-stream"
        if file_path.suffix == ".js":
            mime_type = "application/javascript"
        elif file_path.suffix == ".css":
            mime_type = "text/css"
        elif file_path.suffix == ".html":
            mime_type = "text/html; charset=utf-8"

        try:
            with open(file_path, "rb") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_json({"error": f"Failed reading file: {str(e)}"}, status=500)

def run_server():
    # Ensure database is initialized
    database.init_db()

    STATIC_DIR.mkdir(parents=True, exist_ok=True)

    server = ThreadingHTTPServer((HOST, PORT), ElevoraRequestHandler)
    print(f"\n==================================================================")
    print(f"  ELEVORA AI - Learn-to-Prove-to-Earn Career Platform")
    print(f"  Turn your potential into opportunity.")
    print(f"==================================================================")
    print(f"  Local URL:        http://localhost:{PORT}")
    print(f"  Network URL:      http://127.0.0.1:{PORT}")
    print(f"  Database Path:    {database.DB_PATH}")
    print(f"  Demo Account:     demo@elevora.ai  (password: elevora2026)")
    print(f"==================================================================\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Elevora server...")
        server.server_close()

if __name__ == "__main__":
    run_server()
