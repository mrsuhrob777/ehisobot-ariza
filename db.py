import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                first_name TEXT,
                last_name TEXT,
                username TEXT,
                region TEXT,
                district TEXT,
                school_number TEXT,
                subscription_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_telegram_id INTEGER UNIQUE,
                topic_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_user(data: dict):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO users
                (telegram_id, first_name, last_name, username, region, district, school_number, subscription_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["telegram_id"],
                data["first_name"],
                data["last_name"],
                data["username"],
                data["region"],
                data["district"],
                data["school_number"],
                data["subscription_type"],
            ),
        )


def is_user_registered(telegram_id: int) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
        return row is not None


def count_users() -> int:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT COUNT(*) FROM users").fetchone()
        return row[0] if row else 0


def save_topic(user_telegram_id: int, topic_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO topics (user_telegram_id, topic_id) VALUES (?, ?)",
            (user_telegram_id, topic_id),
        )


def get_topic_by_user(user_telegram_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT topic_id FROM topics WHERE user_telegram_id = ?",
            (user_telegram_id,),
        ).fetchone()
        return row[0] if row else None


def get_user_by_topic(topic_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT user_telegram_id FROM topics WHERE topic_id = ?",
            (topic_id,),
        ).fetchone()
        return row[0] if row else None
