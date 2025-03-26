#backend/crud.py
from .database import get_connection
from .models import Record
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_user_credentials(login: str, password: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE login = ?", (login,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return False
    return row[0] == hash_password(password)

def create_user(login: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (login, password_hash) VALUES (?, ?)",
                   (login, hash_password(password)))
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT login FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def create_record(record: Record):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO records (
            record_date, last_name, first_name, patronymic, status,
            comment, card_number, organization, manufacturer, work_status, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record.record_date, record.last_name, record.first_name, record.patronymic,
        record.status, record.comment, record.card_number, record.organization,
        record.manufacturer, record.work_status, record.created_by
    ))
    conn.commit()
    record.id = cursor.lastrowid
    conn.close()
    return record

def update_record(record_id: int, record: Record):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE records SET
            record_date = ?, last_name = ?, first_name = ?, patronymic = ?,
            status = ?, comment = ?, card_number = ?, organization = ?,
            manufacturer = ?, work_status = ?
        WHERE id = ?
    """, (
        record.record_date, record.last_name, record.first_name, record.patronymic,
        record.status, record.comment, record.card_number, record.organization,
        record.manufacturer, record.work_status, record_id
    ))
    conn.commit()
    conn.close()

def delete_record(record_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

def get_all_records():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM records")
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    conn.close()
    return [dict(zip(columns, row)) for row in rows]
