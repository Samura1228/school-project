import sqlite3
import json
from datetime import datetime, timedelta

DB_NAME = "economic_sprint.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            streak INTEGER DEFAULT 0,
            last_played TEXT,
            best_score INTEGER DEFAULT 0,
            language TEXT DEFAULT 'en'
        )
    ''')
    
    # Questions table
    # We will drop the old table if it exists to update the schema easily
    # In a production app with real data, we would use ALTER TABLE
    cursor.execute("DROP TABLE IF EXISTS questions")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text_en TEXT,
            text_ru TEXT,
            options_en TEXT,
            options_ru TEXT,
            correct_index INTEGER,
            difficulty INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def add_user(user_id, username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Check if user exists to avoid overwriting language preference
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, username, language) VALUES (?, ?, 'en')", (user_id, username))
        conn.commit()
    conn.close()

def get_user_language(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'en'

def set_user_language(user_id, language):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
    conn.commit()
    conn.close()

def update_xp(user_id, xp_gain):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if not result:
        return
        
    current_xp, current_level = result
    new_xp = current_xp + xp_gain
    
    # Level up logic: XP needed = Current Level * 100
    xp_needed = current_level * 100
    new_level = current_level
    
    while new_xp >= xp_needed:
        new_xp -= xp_needed
        new_level += 1
        xp_needed = new_level * 100
        
    cursor.execute("UPDATE users SET xp = ?, level = ? WHERE user_id = ?", (new_xp, new_level, user_id))
    conn.commit()
    conn.close()
    return new_level > current_level # Return True if leveled up

def update_streak(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT last_played, streak FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    today = datetime.now().date().isoformat()
    
    if result:
        last_played, current_streak = result
        
        if last_played == today:
            conn.close()
            return False # Already played today
            
        yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
        
        if last_played == yesterday:
            new_streak = current_streak + 1
        else:
            new_streak = 1
            
        cursor.execute("UPDATE users SET last_played = ?, streak = ? WHERE user_id = ?", (today, new_streak, user_id))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def update_best_score(user_id, score):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT best_score FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result and score > result[0]:
        cursor.execute("UPDATE users SET best_score = ? WHERE user_id = ?", (score, user_id))
        conn.commit()
        
    conn.close()

def get_leaderboard(limit=10):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, level, xp, best_score FROM users ORDER BY level DESC, xp DESC LIMIT ?", (limit,))
    leaders = cursor.fetchall()
    conn.close()
    return leaders

def add_question(text_en, text_ru, options_en, options_ru, correct_index, difficulty):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    options_en_json = json.dumps(options_en)
    options_ru_json = json.dumps(options_ru)
    cursor.execute("INSERT INTO questions (text_en, text_ru, options_en, options_ru, correct_index, difficulty) VALUES (?, ?, ?, ?, ?, ?)", 
                   (text_en, text_ru, options_en_json, options_ru_json, correct_index, difficulty))
    conn.commit()
    conn.close()

def get_random_questions(limit=10):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT ?", (limit,))
    questions = cursor.fetchall()
    conn.close()
    
    formatted_questions = []
    for q in questions:
        formatted_questions.append({
            "id": q[0],
            "text_en": q[1],
            "text_ru": q[2],
            "options_en": json.loads(q[3]),
            "options_ru": json.loads(q[4]),
            "correct_index": q[5],
            "difficulty": q[6]
        })
        
    return formatted_questions