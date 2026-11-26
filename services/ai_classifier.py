def classify_learning_level(score_percentage):
    """
    Identifies the student's learning level based on assessment score:
    - basic: < 40%
    - intermediate: 40% to 70% (inclusive)
    - advanced: > 70%
    """
    pct = float(score_percentage)
    if pct < 40.0:
        return "basic"
    elif pct <= 70.0:
        return "intermediate"
    else:
        return "advanced"

def generate_ai_diagnostic_feedback(score_percentage, level, correct_count, total_count, missed_topics=None):
    """
    Synthesizes AI-based qualitative diagnosis and action plan.
    """
    if missed_topics is None:
        missed_topics = []

    level_meta = {
        "basic": {
            "badge_color": "emerald",
            "title": "Basic (Foundational Track)",
            "summary": (
                f"Your diagnostic score was {score_percentage:.1f}% ({correct_count}/{total_count}). "
                "You are at the foundational learning stage. Our AI system has customized your curriculum "
                "with simplified short notes, intuitive visual clips, and guided micro-challenges to solidify your core syntax."
            ),
            "recommendation": "Begin with Topic 1: Python Syntax & Variables. Watch the short clip and review foundational syntax rules."
        },
        "intermediate": {
            "badge_color": "amber",
            "title": "Intermediate (Application Track)",
            "summary": (
                f"Your diagnostic score was {score_percentage:.1f}% ({correct_count}/{total_count}). "
                "You demonstrated a solid understanding of fundamental programming concepts with room to master "
                "edge-cases, built-in data structures, and modular function design."
            ),
            "recommendation": "Focus on data manipulation and loop optimizations. Dive into intermediate practical examples and common pitfalls."
        },
        "advanced": {
            "badge_color": "indigo",
            "title": "Advanced (Mastery & Optimization Track)",
            "summary": (
                f"Impressive! Your diagnostic score was {score_percentage:.1f}% ({correct_count}/{total_count}). "
                "You possess strong grasp of Python structures and logic. The platform has unlocked high-tier "
                "deep-dive notes covering internals, generators, closures, and algorithmic optimization."
            ),
            "recommendation": "Tackle advanced architectural patterns, memory efficiency with generators, and idiomatic Pythonic idioms."
        }
    }

    meta = level_meta.get(level, level_meta["basic"])
    
    strengths = []
    weaknesses = []

    if level == "basic":
        strengths.append("Eagerness to build structured coding foundations")
        strengths.append("Exposure to basic computational concepts")
        weaknesses.append("Syntax muscle memory & basic data type identification")
        weaknesses.append("Understanding code execution flow in conditional branches")
    elif level == "intermediate":
        strengths.append("Good grasp of arithmetic, variables, and sequential execution")
        strengths.append("Able to trace basic loops and conditionals")
        weaknesses.append("Complex slicing, dictionary key operations, and error handling")
        weaknesses.append("Writing concise functional abstractions and comprehensions")
    else:
        strengths.append("Strong analytical code comprehension and execution tracing")
        strengths.append("Confident usage of composite data structures and higher-order logic")
        weaknesses.append("Deep internal runtime quirks and edge-case exceptions")
        weaknesses.append("Micro-optimizations and generator pipeline architectures")

    if missed_topics:
        weaknesses.extend([f"Needs review: {t}" for t in missed_topics[:2]])

    return {
        "level": level,
        "title": meta["title"],
        "summary": meta["summary"],
        "recommendation": meta["recommendation"],
        "strengths": strengths,
        "weaknesses": weaknesses
    }
