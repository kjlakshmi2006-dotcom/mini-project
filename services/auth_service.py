import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db

def register_user(username, email, password):
    username = username.strip()
    email = email.strip().lower()
    
    if not username or not email or not password:
        return False, "All fields are required."
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
        
    password_hash = generate_password_hash(password)
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, learning_level, diagnostic_completed)
            VALUES (?, ?, ?, 'undetermined', 0)
        """, (username, email, password_hash))
        conn.commit()
        user_id = cursor.lastrowid
        return True, {"id": user_id, "username": username, "email": email}
    except sqlite3.IntegrityError as e:
        err_msg = str(e).lower()
        if "username" in err_msg:
            return False, "Username is already taken."
        elif "email" in err_msg:
            return False, "Email address is already registered."
        return False, "Account already exists."
    finally:
        conn.close()

def authenticate_user(username_or_email, password):
    query = username_or_email.strip()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM users 
        WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)
    """, (query, query))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return False, "Invalid username/email or password."

    if not check_password_hash(user["password_hash"], password):
        return False, "Invalid username/email or password."

    return True, dict(user)

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, learning_level, diagnostic_completed, created_at FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def update_user_level(user_id, level, diagnostic_completed=True):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET learning_level = ?, diagnostic_completed = ?
        WHERE id = ?
    """, (level, 1 if diagnostic_completed else 0, user_id))
    conn.commit()
    conn.close()
