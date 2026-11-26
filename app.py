import os
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify
)
import config
from database.db import init_db
from database.seed_data import seed_database
from services.auth_service import (
    register_user, authenticate_user, get_user_by_id
)
from services.quiz_service import (
    get_diagnostic_questions, get_topic_questions,
    evaluate_diagnostic_quiz, evaluate_topic_quiz
)
from services.adaptive_engine import (
    get_adaptive_material, get_curriculum_status,
    get_next_recommended_topic
)
from services.report_service import get_student_performance_data

app = Flask(__name__)
app.config.from_object(config)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_user():
    current_user = None
    if "user_id" in session:
        current_user = get_user_by_id(session["user_id"])
    return dict(current_user=current_user)

# ----------------- AUTHENTICATION -----------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        success, result = register_user(username, email, password)
        if success:
            session["user_id"] = result["id"]
            session["username"] = result["username"]
            flash(f"Welcome to AdaptLearn, {result['username']}! Let's get started.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash(result, "danger")

    return render_template("auth/register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "")
        password = request.form.get("password", "")

        success, result = authenticate_user(identifier, password)
        if success:
            session["user_id"] = result["id"]
            session["username"] = result["username"]
            session["learning_level"] = result["learning_level"]
            flash(f"Welcome back, {result['username']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash(result, "danger")

    return render_template("auth/login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("login"))

# ----------------- DASHBOARD & SUBJECT SELECTION -----------------

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    user = get_user_by_id(session["user_id"])
    session["learning_level"] = user["learning_level"]

    # Curriculum status for Python (subject_id = 1)
    curriculum = get_curriculum_status(user["id"], subject_id=1)
    next_topic, next_topic_reason = get_next_recommended_topic(user["id"], subject_id=1)

    return render_template(
        "dashboard/index.html",
        user=user,
        curriculum=curriculum,
        next_topic=next_topic,
        next_topic_reason=next_topic_reason
    )

# ----------------- DIAGNOSTIC QUIZ -----------------

@app.route("/quiz/diagnostic")
@login_required
def diagnostic_quiz():
    user = get_user_by_id(session["user_id"])
    questions = get_diagnostic_questions()
    return render_template("quiz/diagnostic.html", user=user, questions=questions)

@app.route("/api/quiz/diagnostic/submit", methods=["POST"])
@login_required
def submit_diagnostic_quiz():
    data = request.get_json() or {}
    answers = data.get("answers", {})

    evaluation = evaluate_diagnostic_quiz(session["user_id"], answers)
    session["learning_level"] = evaluation["assigned_level"]

    return jsonify({
        "success": True,
        "evaluation": evaluation,
        "redirect_url": url_for("diagnostic_result", attempt_id=evaluation["attempt_id"])
    })

@app.route("/quiz/diagnostic/result/<int:attempt_id>")
@login_required
def diagnostic_result(attempt_id):
    user = get_user_by_id(session["user_id"])
    from database.db import get_db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT score_percentage, correct_answers, total_questions, assigned_level, completed_at
        FROM quiz_attempts
        WHERE id = ? AND user_id = ?
    """, (attempt_id, user["id"]))
    attempt = cursor.fetchone()

    cursor.execute("""
        SELECT ai_feedback_summary, strengths, weaknesses, recommended_next_topic
        FROM performance_reports
        WHERE attempt_id = ? AND user_id = ?
    """, (attempt_id, user["id"]))
    report = cursor.fetchone()
    conn.close()

    if not attempt:
        flash("Diagnostic attempt record not found.", "warning")
        return redirect(url_for("dashboard"))

    return render_template(
        "quiz/diagnostic_result.html",
        user=user,
        attempt=dict(attempt),
        report=dict(report) if report else None
    )

# ----------------- ADAPTIVE LEARNING MATERIALS -----------------

@app.route("/learn/<int:topic_id>")
@login_required
def learn_material(topic_id):
    user = get_user_by_id(session["user_id"])
    material_data = get_adaptive_material(user["id"], topic_id)

    if not material_data or not material_data["topic"]:
        flash("Topic material not found.", "danger")
        return redirect(url_for("dashboard"))

    return render_template(
        "learning/material_view.html",
        user=user,
        data=material_data
    )

# ----------------- TOPIC MICRO-ASSESSMENT -----------------

@app.route("/quiz/topic/<int:topic_id>")
@login_required
def topic_quiz(topic_id):
    user = get_user_by_id(session["user_id"])
    material_data = get_adaptive_material(user["id"], topic_id)
    questions = get_topic_questions(topic_id)

    if not questions:
        flash("No questions available for this topic yet.", "info")
        return redirect(url_for("learn_material", topic_id=topic_id))

    return render_template(
        "quiz/topic_quiz.html",
        user=user,
        topic=material_data["topic"],
        questions=questions
    )

@app.route("/api/quiz/topic/<int:topic_id>/submit", methods=["POST"])
@login_required
def submit_topic_quiz(topic_id):
    data = request.get_json() or {}
    answers = data.get("answers", {})

    evaluation = evaluate_topic_quiz(session["user_id"], topic_id, answers)

    # Check if course is now fully completed
    curriculum = get_curriculum_status(session["user_id"], subject_id=1)
    is_fully_completed = curriculum["is_curriculum_completed"]

    return jsonify({
        "success": True,
        "evaluation": evaluation,
        "is_course_completed": is_fully_completed,
        "completion_url": url_for("completion_view") if is_fully_completed else None
    })

# ----------------- PERFORMANCE REPORTS & COMPLETION -----------------

@app.route("/reports")
@login_required
def reports():
    user = get_user_by_id(session["user_id"])
    perf_data = get_student_performance_data(user["id"])
    return render_template("dashboard/reports.html", perf=perf_data)

@app.route("/completion")
@login_required
def completion_view():
    user = get_user_by_id(session["user_id"])
    curriculum = get_curriculum_status(user["id"], subject_id=1)
    perf_data = get_student_performance_data(user["id"])

    return render_template(
        "learning/completion.html",
        user=user,
        curriculum=curriculum,
        perf=perf_data
    )

if __name__ == "__main__":
    init_db()
    seed_database()
    print("AdaptLearn server starting on http://127.0.0.1:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)
