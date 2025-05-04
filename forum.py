import db
import hashlib
import os
import sqlite3

def hash_password(password):
    salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt + hashed_password

def verify_password(stored_password, provided_password):
    salt = stored_password[:16]
    stored_hash = stored_password[16:]
    provided_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
    return stored_hash == provided_hash

def add_user(username, password):
    password_hash = hash_password(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def get_user(username):
    sql = "SELECT id, username, password_hash FROM users WHERE username = ?"
    return db.query(sql, [username])[0]

def get_threads():
    sql = """SELECT t.id, t.title, COUNT(m.id) total, MAX(m.sent_at) last, g.name tag_name
             FROM threads t
             LEFT JOIN messages m ON t.id = m.thread_id
             LEFT JOIN tags g ON t.tag_id = g.id
             GROUP BY t.id
             ORDER BY t.id DESC"""
    return db.query(sql)

def get_thread(thread_id):
    sql = """SELECT t.id, t.title, g.name tag_name
             FROM threads t
             LEFT JOIN tags g ON t.tag_id = g.id
             WHERE t.id = ?"""
    return db.query(sql, [thread_id])[0]

def get_messages(thread_id):
    sql = """SELECT m.id, m.content, m.sent_at, m.user_id, u.username
             FROM messages m, users u
             WHERE m.user_id = u.id AND m.thread_id = ?
             ORDER BY m.id"""
    return db.query(sql, [thread_id])

def get_message(message_id):
    sql = "SELECT id, content, user_id, thread_id FROM messages WHERE id = ?"
    return db.query(sql, [message_id])[0]

def add_thread(title, content, user_id):
    sql = "INSERT INTO threads (title, user_id) VALUES (?, ?)"
    db.execute(sql, [title, user_id])
    thread_id = db.last_insert_id()
    add_message(content, user_id, thread_id)
    return thread_id

def add_message(content, user_id, thread_id):
    sql = """INSERT INTO messages (content, sent_at, user_id, thread_id) VALUES
             (?, datetime('now'), ?, ?)"""
    db.execute(sql, [content, user_id, thread_id])

def update_message(message_id, content):
    sql = "UPDATE messages SET content = ? WHERE id = ?"
    db.execute(sql, [content, message_id])

def remove_message(message_id):
    sql = "DELETE FROM messages WHERE id = ?"
    db.execute(sql, [message_id])


def search(query):
    sql = """
    SELECT DISTINCT m.id AS message_id,
                    m.thread_id,
                    t.title AS thread_title,
                    m.sent_at,
                    u.username,
                    g.name AS tag_name
    FROM threads t
    LEFT JOIN messages m ON t.id = m.thread_id
    LEFT JOIN users u ON u.id = m.user_id
    LEFT JOIN tags g ON t.tag_id = g.id
    WHERE m.content LIKE ? OR
          t.title LIKE ? OR
          u.username LIKE ? OR
          g.name LIKE ?
    ORDER BY m.sent_at DESC
    """
    like_query = "%" + query + "%"
    return db.query(sql, [like_query, like_query, like_query, like_query])


def get_user_by_id(user_id):
    sql = "SELECT id, username, profile_image, bio FROM users WHERE id = ?"
    return db.query(sql, [user_id])[0]

def get_user_threads(user_id):
    sql = "SELECT id, title FROM threads WHERE user_id = ?"
    return db.query(sql, [user_id])

def get_user_messages(user_id):
    sql = """SELECT m.id, m.content, m.thread_id
             FROM messages m
             WHERE m.user_id = ?
             ORDER BY m.sent_at DESC"""
    return db.query(sql, [user_id])

def get_user_stats(user_id):
    sql_threads = "SELECT COUNT(*) FROM threads WHERE user_id = ?"
    sql_messages = "SELECT COUNT(*) FROM messages WHERE user_id = ?"
    thread_count = db.query(sql_threads, [user_id])[0]['COUNT(*)']
    message_count = db.query(sql_messages, [user_id])[0]['COUNT(*)']
    return thread_count, message_count

def update_profile(user_id, profile_image, bio):
    sql = "UPDATE users SET profile_image = ?, bio = ? WHERE id = ?"
    db.execute(sql, [profile_image, bio, user_id])


def add_tag(name):
    sql = "INSERT INTO tags (name) VALUES (?)"
    try:
        db.execute(sql, [name])
    except sqlite3.IntegrityError:
        pass 

def get_tag_id(name):
    sql = "SELECT id FROM tags WHERE name = ?"
    result = db.query(sql, [name])
    if result:
        return result[0]['id']
    return None

def add_thread(title, content, user_id, tag_name=None):
    if tag_name:
        add_tag(tag_name)
        tag_id = get_tag_id(tag_name)
    else:
        tag_id = None

    sql = "INSERT INTO threads (title, user_id, tag_id) VALUES (?, ?, ?)"
    db.execute(sql, [title, user_id, tag_id])
    thread_id = db.last_insert_id()
    add_message(content, user_id, thread_id)
    return thread_id


def get_threads_paginated(offset, limit):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM threads")
    total_threads = cursor.fetchone()[0]

    cursor.execute("""SELECT t.id, t.title, COUNT(m.id) total, MAX(m.sent_at) last, g.name tag_name
                      FROM threads t
                      LEFT JOIN messages m ON t.id = m.thread_id
                      LEFT JOIN tags g ON t.tag_id = g.id
                      GROUP BY t.id
                      ORDER BY t.id DESC
                      LIMIT ? OFFSET ?""", (limit, offset))
    threads = cursor.fetchall()
    conn.close()

    return threads, total_threads


def get_recent_threads(limit=5):
    sql = """SELECT t.id, t.title, MAX(m.sent_at) AS last_message
             FROM threads t
             LEFT JOIN messages m ON t.id = m.thread_id
             GROUP BY t.id
             ORDER BY last_message DESC
             LIMIT ?"""
    return db.query(sql, [limit])


def get_user_role(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def update_user_role(user_id, role):
    sql = "INSERT OR REPLACE INTO user_roles (user_id, role) VALUES (?, ?)"
    db.execute(sql, [user_id, role])
