# export_utils.py
from openpyxl import Workbook
from datetime import datetime

def export_transactions_to_excel(transactions, filename="История_транзакций.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Транзакции"
    headers = ["ID", "Отправитель", "Получатель", "Сумма", "Описание", "Дата"]
    ws.append(headers)
    for t in transactions:
        date_str = t[5].strftime("%d.%m.%Y %H:%M") if isinstance(t[5], datetime) else str(t[5])
        ws.append([
            t[0],
            t[1] or "",
            t[2] or "",
            f"{t[3]:,.2f} ₽",
            t[4] or "",
            date_str
        ])
    wb.save(filename)
    return filename