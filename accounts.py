# accounts.py
import pyodbc
from config import DB_CONFIG
import random
import string

def get_connection():
    conn_str = (
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']}"
    )
    return pyodbc.connect(conn_str)

def generate_account_number():
    return ''.join(random.choices(string.digits, k=16))

def create_account(user_id, account_type='текущий'):
    acc_num = generate_account_number()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Счета (ID_пользователя, Номер_счета, Тип_счета)
            VALUES (?, ?, ?)
        """, (user_id, acc_num, account_type))
        conn.commit()
        conn.close()
        return acc_num
    except Exception as e:
        print(f"Ошибка создания счёта: {e}")
        return None

def get_accounts_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ID_счета, Номер_счета, Баланс, Тип_счета 
        FROM Счета 
        WHERE ID_пользователя = ?
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def transfer_money(from_acc, to_acc, amount, description="Перевод средств"):
    if amount <= 0:
        return False
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Баланс FROM Счета WHERE Номер_счета = ?", (from_acc,))
        from_bal = cursor.fetchone()
        if not from_bal or from_bal[0] < amount:
            return False
        cursor.execute("UPDATE Счета SET Баланс = Баланс - ? WHERE Номер_счета = ?", (amount, from_acc))
        cursor.execute("UPDATE Счета SET Баланс = Баланс + ? WHERE Номер_счета = ?", (amount, to_acc))
        cursor.execute("""
            INSERT INTO Транзакции (Счет_отправителя, Счет_получателя, Сумма, Описание)
            VALUES (?, ?, ?, ?)
        """, (from_acc, to_acc, amount, description))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return False

def get_transaction_history(account_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ID_транзакции, Счет_отправителя, Счет_получателя, Сумма, Описание, Дата_транзакции
        FROM Транзакции
        WHERE Счет_отправителя = ? OR Счет_получателя = ?
        ORDER BY Дата_транзакции DESC
    """, (account_number, account_number))
    rows = cursor.fetchall()
    conn.close()
    return rows