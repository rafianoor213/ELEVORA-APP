"""
ELEVORA AI - Automated Backend & REST API Verification Suite
Tests database initialization, seed data, API route computations, and AI evaluation logic.
"""

import sys
import json
import sqlite3
import database
import ai_service

def run_tests():
    print(">>> 1. Testing Database Initialization...")
    database.init_db(force_reset=True)
    conn = database.get_db_connection()
    cursor = conn.cursor()

    user = cursor.execute("SELECT * FROM users WHERE email = 'demo@elevora.ai'").fetchone()
    assert user is not None, "Demo user should exist!"
    assert user["full_name"] == "Alex Chen", "User name should be Alex Chen!"
    print("   ✓ Demo user Alex Chen verified.")

    skills = cursor.execute("SELECT * FROM user_skills WHERE user_id = ?", (user["id"],)).fetchall()
    assert len(skills) >= 4, "Initial user should have seeded skills!"
    print(f"   ✓ User skills verified ({len(skills)} skills found).")

    jobs = cursor.execute("SELECT * FROM job_listings").fetchall()
    assert len(jobs) >= 5, "Sample jobs dataset should be populated!"
    print(f"   ✓ Job listings verified ({len(jobs)} jobs found).")

    roadmap = cursor.execute("SELECT * FROM learning_roadmap").fetchall()
    assert len(roadmap) >= 5, "Roadmap lessons should be populated!"
    print(f"   ✓ Learning roadmap verified ({len(roadmap)} lessons found).")

    print("\n>>> 2. Testing Skill-Gap Analysis Algorithm...")
    user_skills_list = [dict(s) for s in skills]
    req_skills = ["HTML5", "CSS3", "JavaScript", "Responsive Design", "Git & GitHub"]
    pref_skills = ["React", "API Integration"]

    gap_res = ai_service.calculate_skill_gap_analysis(user_skills_list, req_skills, pref_skills)
    assert "match_percentage" in gap_res, "Match percentage should be returned!"
    assert "readiness_percentage" in gap_res, "Readiness percentage should be returned!"
    print(f"   ✓ Initial Match Score: {gap_res['match_percentage']}%")
    print(f"   ✓ Initial Career Readiness: {gap_res['readiness_percentage']}%")
    print(f"   ✓ Missing Essential: {[m['name'] for m in gap_res['essential_missing']]}")

    print("\n>>> 3. Testing Practical Project & Rubric Evaluation...")
    submission = {
        "submission_title": "Interactive Task Management Web Application",
        "live_url": "https://alexchen-taskflow.vercel.app",
        "github_url": "https://github.com/alexchen/taskflow-pro",
        "description": "A responsive task management app built with semantic HTML5, modern CSS flexbox & grid, and vanilla JavaScript managing state and LocalStorage.",
        "architecture_notes": "Implemented MVC state pattern with dynamic DOM event delegation and persistent Web Storage."
    }
    eval_res = ai_service.evaluate_project_submission({}, submission)
    assert eval_res["total_score"] >= 50, "Evaluation should score verified project accurately!"
    assert "grade" in eval_res, "Grade should be present!"
    assert len(eval_res["strengths"]) > 0, "Strengths should be provided!"
    assert len(eval_res["improvements"]) > 0, "Areas for improvement should be provided!"
    print(f"   ✓ Rubric Score: {eval_res['total_score']}/{eval_res['max_score']} ({eval_res['percentage']}%) - Grade: {eval_res['grade']}")
    print(f"   ✓ Unlocked Demonstrated Skills: {eval_res['demonstrated_skills_unlocked']}")

    print("\n>>> 4. Testing Rule-Based Career Advisory Fallback...")
    advice = ai_service.get_career_advice("What skills do I need next?", dict(user))
    assert "message" in advice, "Advice message should be generated!"
    assert "Frontend Developer" in advice["target_career"], "Target career should be reflected!"
    print("   ✓ Career Advisor response generated cleanly.")

    print("\n>>> 5. Testing Demo Reset...")
    database.reset_demo_user()
    reset_user = cursor.execute("SELECT * FROM users WHERE email = 'demo@elevora.ai'").fetchone()
    assert reset_user["full_name"] == "Alex Chen"
    print("   ✓ Demo reset successfully verified.")

    conn.close()
    print("\n========================================================")
    print(" ALL BACKEND & LOGIC VERIFICATION CHECKS PASSED (100%) ")
    print("========================================================\n")

if __name__ == "__main__":
    run_tests()
