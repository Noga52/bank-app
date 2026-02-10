import pyodbc
from config import DB_CONFIG

def get_connection():
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']}"
    )
    return pyodbc.connect(conn_str)

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ID_пользователя, Логин, ФИО, Роль FROM Пользователи")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Пользователи WHERE ID_пользователя = ?", (user_id,))
    conn.commit()
    conn.close()
    return True