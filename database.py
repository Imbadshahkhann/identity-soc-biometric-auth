import sqlite3
import os

DB_PATH = "users.db"

def init_db():
    """Initializes the SQLite database for storing users and auth logs."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            encrypted_encoding BLOB NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auth_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL,
            match_score REAL,
            system_ip TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, encrypted_encoding):
    """Adds a new user with their encrypted biometric template."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, encrypted_encoding) 
            VALUES (?, ?)
        ''', (username, encrypted_encoding))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    """Retrieves a user's encrypted biometric template by username."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT encrypted_encoding FROM users WHERE username = ?
    ''', (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]
    return None

def log_auth_attempt(username, status, match_score=None, system_ip=None):
    """Logs an authentication attempt."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO auth_logs (username, status, match_score, system_ip) 
        VALUES (?, ?, ?, ?)
    ''', (username, status, match_score, system_ip))
    conn.commit()
    conn.close()

def get_all_users():
    """Retrieves all registered users."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username FROM users')
    result = cursor.fetchall()
    conn.close()
    return [{'id': row[0], 'username': row[1]} for row in result]

def get_auth_logs():
    """Retrieves all authentication logs."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, timestamp, status, match_score, system_ip FROM auth_logs ORDER BY timestamp DESC')
    result = cursor.fetchall()
    conn.close()
    return [{'id': row[0], 'username': row[1], 'timestamp': row[2], 'status': row[3], 'match_score': row[4], 'system_ip': row[5]} for row in result]

def delete_user(username):
    """Deletes a user from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted
