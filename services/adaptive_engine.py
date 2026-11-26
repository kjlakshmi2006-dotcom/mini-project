from database.db import get_db

def get_adaptive_material(user_id, topic_id):
    """
    Returns learning material tailored strictly to the student's assigned learning level.
    If no level is assigned yet, defaults to 'basic'.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Get student's current learning level
    cursor.execute("SELECT learning_level FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    level = user["learning_level"] if (user and user["learning_level"] in ("basic", "intermediate", "advanced")) else "basic"

    # Fetch topic info
    cursor.execute("SELECT id, subject_id, title, sequence_order, description FROM topics WHERE id = ?", (topic_id,))
    topic = cursor.fetchone()
    if not topic:
        conn.close()
        return None

    # Fetch corresponding level material
    cursor.execute("""
        SELECT id, topic_id, level_tier, title, notes_markdown, video_url, video_title,
               duration_minutes, key_takeaways
        FROM learning_materials
        WHERE topic_id = ? AND level_tier = ?
    """, (topic_id, level))
    material = cursor.fetchone()

    # Fallback to any material if exact tier missing
    if not material:
        cursor.execute("SELECT * FROM learning_materials WHERE topic_id = ? LIMIT 1", (topic_id,))
        material = cursor.fetchone()

    # Get topic progress
    cursor.execute("""
        SELECT status, mastery_score, attempts_count 
        FROM student_progress 
        WHERE user_id = ? AND topic_id = ?
    """, (user_id, topic_id))
    prog = cursor.fetchone()

    # Navigation (previous and next topic ids)
    cursor.execute("""
        SELECT id, title FROM topics
        WHERE subject_id = ? AND sequence_order < ?
        ORDER BY sequence_order DESC LIMIT 1
    """, (topic["subject_id"], topic["sequence_order"]))
    prev_topic = cursor.fetchone()

    cursor.execute("""
        SELECT id, title FROM topics
        WHERE subject_id = ? AND sequence_order > ?
        ORDER BY sequence_order ASC LIMIT 1
    """, (topic["subject_id"], topic["sequence_order"]))
    next_topic = cursor.fetchone()

    conn.close()

    return {
        "user_level": level,
        "topic": dict(topic),
        "material": dict(material) if material else None,
        "progress": dict(prog) if prog else {"status": "not_started", "mastery_score": 0.0, "attempts_count": 0},
        "prev_topic": dict(prev_topic) if prev_topic else None,
        "next_topic": dict(next_topic) if next_topic else None
    }

def get_curriculum_status(user_id, subject_id=1):
    """
    Returns full topic list with user progress and calculates curriculum completion percentage.
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.id, t.title, t.sequence_order, t.description,
               COALESCE(sp.status, 'not_started') as status,
               COALESCE(sp.mastery_score, 0.0) as mastery_score,
               COALESCE(sp.attempts_count, 0) as attempts_count
        FROM topics t
        LEFT JOIN student_progress sp ON sp.topic_id = t.id AND sp.user_id = ?
        WHERE t.subject_id = ?
        ORDER BY t.sequence_order ASC
    """, (user_id, subject_id))
    topics = [dict(r) for r in cursor.fetchall()]

    total_topics = len(topics)
    completed_topics = sum(1 for t in topics if t["status"] == "completed")
    completion_percentage = (completed_topics / total_topics * 100.0) if total_topics > 0 else 0.0

    conn.close()

    return {
        "topics": topics,
        "total_topics": total_topics,
        "completed_topics": completed_topics,
        "completion_percentage": round(completion_percentage, 1),
        "is_curriculum_completed": (completed_topics == total_topics and total_topics > 0)
    }

def get_next_recommended_topic(user_id, subject_id=1):
    """
    Identifies the ideal next topic to study based on adaptive state:
    1. Highest priority: Any topic flagged 'remedial'
    2. Next: Topic flagged 'in_progress'
    3. Next: First topic 'not_started'
    4. If all completed, return None (course complete!)
    """
    curriculum = get_curriculum_status(user_id, subject_id)
    topics = curriculum["topics"]

    # 1. Check remedial
    for t in topics:
        if t["status"] == "remedial":
            return t, "remedial_review"

    # 2. Check in_progress
    for t in topics:
        if t["status"] == "in_progress":
            return t, "in_progress"

    # 3. Check not_started
    for t in topics:
        if t["status"] == "not_started":
            return t, "new_topic"

    return None, "course_completed"
