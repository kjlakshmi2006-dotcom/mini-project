from database.db import get_db

def get_student_performance_data(user_id):
    """
    Aggregates full performance metrics for the student analytics dashboard:
    - Diagnostic assessment score and classified tier
    - Topic mastery radar chart data
    - Attempt timeline history
    - Latest AI recommendations & feedback
    """
    conn = get_db()
    cursor = conn.cursor()

    # User basic info
    cursor.execute("SELECT id, username, email, learning_level, diagnostic_completed, created_at FROM users WHERE id = ?", (user_id,))
    user = dict(cursor.fetchone())

    # Diagnostic attempt
    cursor.execute("""
        SELECT id, score_percentage, correct_answers, total_questions, assigned_level, completed_at
        FROM quiz_attempts
        WHERE user_id = ? AND is_diagnostic = 1
        ORDER BY id DESC LIMIT 1
    """, (user_id,))
    diag_attempt = cursor.fetchone()
    diag_attempt = dict(diag_attempt) if diag_attempt else None

    # Topic Progress
    cursor.execute("""
        SELECT t.id, t.title, t.sequence_order,
               COALESCE(sp.status, 'not_started') as status,
               COALESCE(sp.mastery_score, 0.0) as mastery_score,
               COALESCE(sp.attempts_count, 0) as attempts_count,
               sp.last_accessed
        FROM topics t
        LEFT JOIN student_progress sp ON sp.topic_id = t.id AND sp.user_id = ?
        WHERE t.subject_id = 1
        ORDER BY t.sequence_order ASC
    """, (user_id,))
    topics_progress = [dict(r) for r in cursor.fetchall()]

    # All attempts for score timeline
    cursor.execute("""
        SELECT qa.id, qa.is_diagnostic, qa.score_percentage, qa.completed_at,
               COALESCE(t.title, 'Diagnostic Assessment') as assessment_name
        FROM quiz_attempts qa
        LEFT JOIN topics t ON qa.topic_id = t.id
        WHERE qa.user_id = ?
        ORDER BY qa.completed_at ASC
    """, (user_id,))
    attempts_history = [dict(r) for r in cursor.fetchall()]

    # Latest AI Performance Report
    cursor.execute("""
        SELECT ai_feedback_summary, strengths, weaknesses, recommended_next_topic, generated_at
        FROM performance_reports
        WHERE user_id = ?
        ORDER BY id DESC LIMIT 1
    """, (user_id,))
    report_row = cursor.fetchone()
    latest_report = dict(report_row) if report_row else None

    conn.close()

    # Chart datasets preparation
    radar_labels = [t["title"] for t in topics_progress]
    radar_scores = [round(t["mastery_score"], 1) for t in topics_progress]

    timeline_labels = [a["assessment_name"] for a in attempts_history]
    timeline_scores = [round(a["score_percentage"], 1) for a in attempts_history]

    # Calculate overall average
    all_scores = [a["score_percentage"] for a in attempts_history]
    average_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0.0

    completed_count = sum(1 for t in topics_progress if t["status"] == "completed")
    total_topics = len(topics_progress)
    progress_pct = round((completed_count / total_topics * 100.0), 1) if total_topics > 0 else 0.0

    return {
        "user": user,
        "diagnostic_attempt": diag_attempt,
        "topics_progress": topics_progress,
        "attempts_history": attempts_history,
        "latest_report": latest_report,
        "average_score": average_score,
        "progress_pct": progress_pct,
        "completed_count": completed_count,
        "total_topics": total_topics,
        "chart_data": {
            "radar": {
                "labels": radar_labels,
                "scores": radar_scores
            },
            "timeline": {
                "labels": timeline_labels,
                "scores": timeline_scores
            }
        }
    }
