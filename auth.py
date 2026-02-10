import pyodbc
from config import DB_CONFIG
import hashlib

def get_connection():
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']}"
    )
    return pyodbc.connect(conn_str)

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(login, password, fio, role):
    if role not in ('клиент', 'сотрудник', 'администратор'):
        raise ValueError("Недопустимая роль")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Пользователи (Логин, Хеш_пароля, ФИО, Роль)
            VALUES (?, ?, ?, ?)
        """, (login, hash_password(password), fio, role))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Ошибка регистрации: {e}")
        return False

def authenticate_user(login, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ID_пользователя, Роль 
            FROM Пользователи 
            WHERE Логин = ? AND Хеш_пароля = ?
        """, (login, hash_password(password)))
        row = cursor.fetchone()
        conn.close()
        return row  # (ID, роль) или None
    except Exception as e:
        print(f"Ошибка входа: {e}")
        return None