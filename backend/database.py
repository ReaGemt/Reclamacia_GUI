import sqlite3
from .config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Таблица записей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_date TEXT,
            last_name TEXT,
            first_name TEXT,
            patronymic TEXT,
            status TEXT,
            comment TEXT,
            card_number TEXT,
            organization TEXT,
            manufacturer TEXT,
            work_status TEXT,
            created_by TEXT
        )
    """)

    # Добавление поля created_by при обновлении базы
    cursor.execute("PRAGMA table_info(records)")
    columns = [col[1] for col in cursor.fetchall()]
    if "created_by" not in columns:
        cursor.execute("ALTER TABLE records ADD COLUMN created_by TEXT")

    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
