import sqlite3
import hashlib
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()
def check_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    hashed_pwd = make_hashes(password)
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_pwd))
    data = cursor.fetchone()
    conn.close()
    return data
def add_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    hashed_pwd = make_hashes(password)
    try:
        cursor.execute('INSERT INTO users(username, password) VALUES (?,?)', (username, hashed_pwd))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False  # Username pehle se exist karta hai
    conn.close()
    return success