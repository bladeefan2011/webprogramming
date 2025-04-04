import db
import hashlib
import os

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
    sql = """SELECT t.id, t.title, COUNT(m.id) total, MAX(m.sent_at) last
             FROM threads t, messages m
             WHERE t.id = m.thread_id
             GROUP BY t.id
             ORDER BY t.id DESC"""
    return db.query(sql)

def get_thread(thread_id):
    sql = "SELECT id, title FROM threads WHERE id = ?"
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
    sql = """SELECT m.id message_id,
                    m.thread_id,
                    t.title thread_title,
                    m.sent_at,
                    u.username
             FROM threads t, messages m, users u
             WHERE t.id = m.thread_id AND
                   u.id = m.user_id AND
                   m.content LIKE ?
             ORDER BY m.sent_at DESC"""
    return db.query(sql, ["%" + query + "%"])
