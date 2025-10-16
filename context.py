import sqlite3
import hashlib
import os
from typing import Optional

DB_FN = "password_context.db"

class ContextDB:
    def __init__(self, db_path=DB_FN):
        self.db_path = db_path
        init_needed = not os.path.exists(db_path)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        if init_needed: self._init_db()

    def _init_db(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE user_passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            pw_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
        cur.execute("""
        CREATE TABLE user_mfa (
            user_id TEXT PRIMARY KEY,
            mfa_enabled INTEGER DEFAULT 0
        )""")
        self.conn.commit()

    def store_password(self, user_id: str, password: str):
        h = hashlib.sha256(password.encode("utf-8")).hexdigest()
        cur = self.conn.cursor()
        cur.execute("INSERT INTO user_passwords (user_id, pw_hash) VALUES (?, ?)", (user_id, h))
        self.conn.commit()

    def has_reuse(self, user_id: str, password: str) -> bool:
        h = hashlib.sha256(password.encode("utf-8")).hexdigest()
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(1) FROM user_passwords WHERE user_id = ? AND pw_hash = ?", (user_id, h))
        row = cur.fetchone()
        return row[0] > 0

    def set_mfa(self, user_id: str, enabled: bool):
        cur = self.conn.cursor()
        cur.execute("INSERT OR REPLACE INTO user_mfa (user_id, mfa_enabled) VALUES (?, ?)", (user_id, 1 if enabled else 0))
        self.conn.commit()

    def get_mfa(self, user_id: str) -> Optional[bool]:
        cur = self.conn.cursor()
        cur.execute("SELECT mfa_enabled FROM user_mfa WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return bool(row[0]) if row else None

    def close(self):
        try: self.conn.close()
        except Exception: pass