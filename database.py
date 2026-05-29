import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS generations (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER, 
        prompt TEXT, 
        model TEXT, 
        size TEXT, 
        image_path TEXT, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def add_art(user_id, prompt, style, path):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO generations (user_id, prompt, model, size, image_path) VALUES (?, ?, ?, ?, ?)', 
                   (user_id, prompt, style, "1024x1024", path))
    conn.commit()
    conn.close()

def get_user_gallery(user_id=0):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM generations ORDER BY created_at DESC')
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return items

def get_all_stats():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM generations')
    total = cursor.fetchone()[0]
    conn.close()
    return {"total": total}