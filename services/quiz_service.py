from database.db import get_db
from services.ai_classifier import classify_learning_level, generate_ai_diagnostic_feedback

def get_diagnostic_questions():
    """Fetches the 10 diagnostic questions."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.id, q.topic_id, q.question_text, q.code_snippet,
               q.option_a, q.option_b, q.option_c, q.option_d,
               q.difficulty_tier, t.title as topic_title
        FROM questions q
        LEFT JOIN topics t ON q.topic_id = t.id
        WHERE q.is_diagnostic = 1
        ORDER BY q.id ASC
        LIMIT 10
    """)
    questions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return questions

def get_topic_questions(topic_id, limit=3):
    """Fetches micro-assessment questions for a given topic."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT q.id, q.topic_id, q.question_text, q.code_snippet,
               q.option_a, q.option_b, q.option_c, q.option_d,
               q.difficulty_tier
        FROM questions q
        WHERE q.topic_id = ? AND q.is_diagnostic = 0
        ORDER BY q.id ASC
        LIMIT ?
    """, (topic_id, limit))
    questions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return questions

def evaluate_diagnostic_quiz(user_id, submitted_answers):
    """
    Evaluates submitted answers for the 10 diagnostic questions.
    Stores attempt and responses in SQLite.
    Returns score, level, and AI diagnostic feedback.
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT q.id, q.correct_option, q.explanation, q.topic_id, t.title as topic_title
        FROM questions q
        LEFT JOIN topics t ON q.topic_id = t.id
        WHERE q.is_diagnostic = 1
        ORDER BY q.id ASC
    """)
    questions = cursor.fetchall()

    total_questions = len(questions)
    correct_count = 0
    detailed_results = []
    missed_topics = []

    for q in questions:
        qid = str(q["id"])
        selected = submitted_answers.get(qid, "").strip().upper()
        is_correct = (selected == q["correct_option"])
        if is_correct:
            correct_count += 1
        else:
            if q["topic_title"] and q["topic_title"] not in missed_topics:
                missed_topics.append(q["topic_title"])

        detailed_results.append({
            "question_id": q["id"],
            "selected_option": selected,
            "correct_option": q["correct_option"],
            "is_correct": is_correct,
            "explanation": q["explanation"]
        })

    score_percentage = (correct_count / total_questions * 100.0) if total_questions > 0 else 0.0
    assigned_level = classify_learning_level(score_percentage)

    # Save to quiz_attempts
    cursor.execute("""
        INSERT INTO quiz_attempts (
            user_id, topic_id, is_diagnostic, total_questions,
            correct_answers, score_percentage, assigned_level
        ) VALUES (?, NULL, 1, ?, ?, ?, ?)
    """, (user_id, total_questions, correct_count, score_percentage, assigned_level))
    attempt_id = cursor.lastrowid

    # Save individual responses
    for res in detailed_results:
        cursor.execute("""
            INSERT INTO quiz_responses (attempt_id, question_id, selected_option, is_correct)
            VALUES (?, ?, ?, ?)
        """, (attempt_id, res["question_id"], res["selected_option"], 1 if res["is_correct"] else 0))

    # Update user learning level
    cursor.execute("""
        UPDATE users
        SET learning_level = ?, diagnostic_completed = 1
        WHERE id = ?
    """, (assigned_level, user_id))

    # Generate AI Feedback
    ai_feedback = generate_ai_diagnostic_feedback(
        score_percentage=score_percentage,
        level=assigned_level,
        correct_count=correct_count,
        total_count=total_questions,
        missed_topics=missed_topics
    )

    # Save performance report
    cursor.execute("""
        INSERT INTO performance_reports (
            user_id, attempt_id, ai_feedback_summary, strengths, weaknesses, recommended_next_topic
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        attempt_id,
        ai_feedback["summary"],
        " | ".join(ai_feedback["strengths"]),
        " | ".join(ai_feedback["weaknesses"]),
        ai_feedback["recommendation"]
    ))

    # Initialize first topic progress
    cursor.execute("SELECT id FROM topics WHERE subject_id = 1 ORDER BY sequence_order ASC LIMIT 1")
    first_topic = cursor.fetchone()
    if first_topic:
        cursor.execute("""
            INSERT OR IGNORE INTO student_progress (user_id, topic_id, status, mastery_score, attempts_count)
            VALUES (?, ?, 'in_progress', 0.0, 0)
        """, (user_id, first_topic["id"]))

    conn.commit()
    conn.close()

    return {
        "attempt_id": attempt_id,
        "total_questions": total_questions,
        "correct_count": correct_count,
        "score_percentage": score_percentage,
        "assigned_level": assigned_level,
        "ai_feedback": ai_feedback,
        "results": detailed_results
    }

def evaluate_topic_quiz(user_id, topic_id, submitted_answers):
    """
    Evaluates micro-assessment for a specific topic.
    Updates mastery score and student progress.
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, correct_option, explanation, difficulty_tier
        FROM questions
        WHERE topic_id = ? AND is_diagnostic = 0
        ORDER BY id ASC
    """, (topic_id,))
    questions = cursor.fetchall()

    total_questions = len(questions)
    correct_count = 0
    detailed_results = []

    for q in questions:
        qid = str(q["id"])
        selected = submitted_answers.get(qid, "").strip().upper()
        is_correct = (selected == q["correct_option"])
        if is_correct:
            correct_count += 1

        detailed_results.append({
            "question_id": q["id"],
            "selected_option": selected,
            "correct_option": q["correct_option"],
            "is_correct": is_correct,
            "explanation": q["explanation"]
        })

    score_percentage = (correct_count / total_questions * 100.0) if total_questions > 0 else 0.0
    passed = score_percentage >= 60.0
    status = "completed" if passed else "remedial"

    # Record attempt
    cursor.execute("""
        INSERT INTO quiz_attempts (
            user_id, topic_id, is_diagnostic, total_questions,
            correct_answers, score_percentage, assigned_level
        ) VALUES (?, ?, 0, ?, ?, ?, NULL)
    """, (user_id, topic_id, total_questions, correct_count, score_percentage))
    attempt_id = cursor.lastrowid

    # Record responses
    for res in detailed_results:
        cursor.execute("""
            INSERT INTO quiz_responses (attempt_id, question_id, selected_option, is_correct)
            VALUES (?, ?, ?, ?)
        """, (attempt_id, res["question_id"], res["selected_option"], 1 if res["is_correct"] else 0))

    # Update or insert student_progress
    cursor.execute("""
        INSERT INTO student_progress (user_id, topic_id, status, mastery_score, attempts_count, last_accessed)
        VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id, topic_id) DO UPDATE SET
            status = excluded.status,
            mastery_score = MAX(student_progress.mastery_score, excluded.mastery_score),
            attempts_count = student_progress.attempts_count + 1,
            last_accessed = CURRENT_TIMESTAMP
    """, (user_id, topic_id, status, score_percentage))

    # Determine next topic if passed
    next_topic = None
    if passed:
        cursor.execute("""
            SELECT id, title, sequence_order
            FROM topics
            WHERE subject_id = (SELECT subject_id FROM topics WHERE id = ?)
              AND sequence_order > (SELECT sequence_order FROM topics WHERE id = ?)
            ORDER BY sequence_order ASC
            LIMIT 1
        """, (topic_id, topic_id))
        next_topic_row = cursor.fetchone()
        if next_topic_row:
            next_topic = dict(next_topic_row)
            cursor.execute("""
                INSERT OR IGNORE INTO student_progress (user_id, topic_id, status, mastery_score, attempts_count)
                VALUES (?, ?, 'in_progress', 0.0, 0)
            """, (user_id, next_topic["id"]))

    conn.commit()
    conn.close()

    return {
        "attempt_id": attempt_id,
        "total_questions": total_questions,
        "correct_count": correct_count,
        "score_percentage": score_percentage,
        "passed": passed,
        "status": status,
        "next_topic": next_topic,
        "results": detailed_results
    }
