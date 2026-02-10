import tkinter as tk
from tkinter import messagebox, ttk
from auth import authenticate_user, register_user
from accounts import get_accounts_by_user, transfer_money, get_transaction_history, create_account
from export_utils import export_transactions_to_excel
from calculators import калькулятор_вклада, калькулятор_кредита
from admin_panel import get_all_users, delete_user


class BankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Банковское приложение")
        self.root.geometry("800x600")
        self.current_user_id = None
        self.current_role = None
        self.center_window()
        self.login_screen()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login_screen(self):
        self.clear_window()
        self.root.geometry("400x300")
        self.center_window()

        frame = tk.Frame(self.root)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Авторизация", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=15)
        tk.Label(frame, text="Логин:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.login_entry = tk.Entry(frame, width=25)
        self.login_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Пароль:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.pass_entry = tk.Entry(frame, show="*", width=25)
        self.pass_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(frame, text="Войти", command=self.login, width=20).grid(row=3, column=0, columnspan=2, pady=10)
        tk.Button(frame, text="Регистрация", command=self.register_screen, width=20).grid(row=4, column=0, columnspan=2)

    def register_screen(self):
        self.clear_window()
        self.root.geometry("450x350")
        self.center_window()

        frame = tk.Frame(self.root)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Регистрация", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=15)
        tk.Label(frame, text="Логин:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        login = tk.Entry(frame, width=25);
        login.grid(row=1, column=1)

        tk.Label(frame, text="Пароль:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        passwd = tk.Entry(frame, show="*", width=25);
        passwd.grid(row=2, column=1)

        tk.Label(frame, text="ФИО:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        fio = tk.Entry(frame, width=25);
        fio.grid(row=3, column=1)

        tk.Label(frame, text="Роль:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        role = ttk.Combobox(frame, values=["клиент", "сотрудник"], state="readonly", width=22)
        role.set("клиент")
        role.grid(row=4, column=1)

        def do_register():
            if register_user(login.get(), passwd.get(), fio.get(), role.get()):
                messagebox.showinfo("Успех", "Регистрация прошла успешно!")
                self.login_screen()
            else:
                messagebox.showerror("Ошибка", "Логин уже существует или ошибка БД")

        tk.Button(frame, text="Зарегистрироваться", command=do_register, width=20).grid(row=5, column=0, columnspan=2,
                                                                                        pady=15)
        tk.Button(frame, text="Назад", command=self.login_screen, width=20).grid(row=6, column=0, columnspan=2)

    def login(self):
        user = authenticate_user(self.login_entry.get(), self.pass_entry.get())
        if user:
            self.current_user_id, self.current_role = user
            self.main_menu()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def main_menu(self):
        self.clear_window()
        self.root.geometry("800x600")
        self.center_window()

        # Верхняя панель
        top_frame = tk.Frame(self.root, bg="#f0f0f0", height=50)
        top_frame.pack(side="top", fill="x")

        buttons = [
            ("Мои счета", self.my_accounts),
            ("Управление счетами", self.account_management),
            ("История транзакций", self.transaction_history),
            ("Калькуляторы", self.calculators_view),
        ]
        if self.current_role == "администратор":
            buttons.append(("Админ-панель", self.admin_view))

        for text, cmd in buttons:
            tk.Button(top_frame, text=text, command=cmd, width=18, height=2).pack(side="left", padx=5, pady=5)

        # Основной контент
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Роль в правом нижнем углу
        role_label = tk.Label(self.root, text=f"Роль: {self.current_role}", fg="gray", anchor="se")
        role_label.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")

        self.my_accounts()

    def show_content(self, title, content_func):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        tk.Label(self.content_frame, text=title, font=("Arial", 14, "bold")).pack(pady=10)
        content_func()

    # === Основные экраны ===
    def my_accounts(self):
        self.show_content("Мои банковские счета", self._render_my_accounts)

    def _render_my_accounts(self):
        accounts = get_accounts_by_user(self.current_user_id)
        if accounts:
            for acc in accounts:
                frame = tk.Frame(self.content_frame, relief="groove", bd=1, padx=10, pady=5)
                frame.pack(fill="x", pady=5)
                tk.Label(frame, text=f"Счёт: {acc[1]} | Тип: {acc[3]} | Баланс: {acc[2]:,.2f} ₽").pack(side="left")
                tk.Button(frame, text="Перевод", command=lambda a=acc[1]: self.transfer_screen(a)).pack(side="right")
        else:
            tk.Label(self.content_frame, text="У вас нет счетов.").pack()

    def account_management(self):
        self.show_content("Управление счетами", self._render_account_management)

    def _render_account_management(self):
        accounts = get_accounts_by_user(self.current_user_id)
        if accounts:
            tk.Label(self.content_frame, text="Ваши счета:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
            for acc in accounts:
                tk.Label(
                    self.content_frame,
                    text=f"Счёт {acc[1]} | Тип: {acc[3]} | Баланс: {acc[2]:,.2f} ₽"
                ).pack(anchor="w", padx=10, pady=2)
        else:
            tk.Label(self.content_frame, text="У вас пока нет счетов.").pack()

        tk.Button(
            self.content_frame,
            text="Открыть новый счёт",
            command=self._create_new_account,
            width=25,
            bg="#4CAF50",
            fg="white"
        ).pack(pady=15)

    def _create_new_account(self):
        win = tk.Toplevel(self.root)
        win.title("Новый счёт")
        win.geometry("300x150")
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="Выберите тип счёта:").pack(pady=10)
        acc_type = ttk.Combobox(win, values=["текущий", "вклад", "кредит"], state="readonly")
        acc_type.set("текущий")
        acc_type.pack(pady=5)

        def confirm():
            num = create_account(self.current_user_id, acc_type.get())
            if num:
                messagebox.showinfo("Успех", f"Счёт {num} успешно открыт!")
                win.destroy()
                self.account_management()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать счёт")

        tk.Button(win, text="Создать", command=confirm, width=15).pack(pady=10)

    def transfer_screen(self, from_acc):
        self.show_content(f"Перевод со счёта {from_acc}", lambda: self._render_transfer(from_acc))

    def _render_transfer(self, from_acc):
        tk.Label(self.content_frame, text="Счёт получателя:").pack(anchor="w")
        to_acc = tk.Entry(self.content_frame, width=40);
        to_acc.pack(pady=5)
        tk.Label(self.content_frame, text="Сумма (₽):").pack(anchor="w")
        amount = tk.Entry(self.content_frame, width=40);
        amount.pack(pady=5)
        tk.Label(self.content_frame, text="Описание (необязательно):").pack(anchor="w")
        desc = tk.Entry(self.content_frame, width=40);
        desc.pack(pady=5)

        def do_transfer():
            try:
                amt = float(amount.get())
                if transfer_money(from_acc, to_acc.get(), amt, desc.get() or "Перевод"):
                    messagebox.showinfo("Успех", "Перевод выполнен!")
                    self.my_accounts()
                else:
                    messagebox.showerror("Ошибка", "Недостаточно средств или неверный счёт")
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректная сумма")

        tk.Button(self.content_frame, text="Выполнить перевод", command=do_transfer, width=25).pack(pady=10)
        tk.Button(self.content_frame, text="Отмена", command=self.my_accounts, width=25).pack()

    def transaction_history(self):
        self.show_content("История транзакций", self._render_transaction_history)

    def _render_transaction_history(self):
        accounts = get_accounts_by_user(self.current_user_id)
        if not accounts:
            tk.Label(self.content_frame, text="Нет счетов для просмотра истории").pack()
            return
        acc_num = accounts[0][1]
        history = get_transaction_history(acc_num)
        if history:
            for t in history[:15]:
                date_str = t[5].strftime('%d.%m.%Y %H:%M') if hasattr(t[5], 'strftime') else str(t[5])
                tk.Label(
                    self.content_frame,
                    text=f"{date_str} | {t[1] or '—'} → {t[2] or '—'} | {t[3]:,.2f} ₽ | {t[4] or ''}",
                    anchor="w",
                    justify="left"
                ).pack(anchor="w", pady=2)
            if messagebox.askyesno("Экспорт", "Сохранить историю в Excel?"):
                file = export_transactions_to_excel(history)
                messagebox.showinfo("Экспорт", f"Файл сохранён: {file}")
        else:
            tk.Label(self.content_frame, text="Транзакций нет").pack()

    def calculators_view(self):
        self.show_content("Калькуляторы", self._render_calculators)

    def _render_calculators(self):
        tk.Label(self.content_frame, text="Калькулятор вклада", font=("Arial", 12, "bold")).pack(anchor="w",
                                                                                                 pady=(10, 5))
        tk.Label(self.content_frame, text="Сумма (₽):").pack(anchor="w")
        dep_sum = tk.Entry(self.content_frame, width=30);
        dep_sum.pack()
        tk.Label(self.content_frame, text="Ставка (% годовых):").pack(anchor="w")
        dep_rate = tk.Entry(self.content_frame, width=30);
        dep_rate.pack()
        tk.Label(self.content_frame, text="Срок (месяцев):").pack(anchor="w")
        dep_months = tk.Entry(self.content_frame, width=30);
        dep_months.pack()

        def calc_deposit():
            try:
                s = float(dep_sum.get())
                r = float(dep_rate.get())
                m = int(dep_months.get())
                res = калькулятор_вклада(s, r, m)
                messagebox.showinfo("Результат", f"Итоговая сумма: {res:,.2f} ₽")
            except:
                messagebox.showerror("Ошибка", "Проверьте введённые данные")

        tk.Button(self.content_frame, text="Рассчитать вклад", command=calc_deposit, width=25).pack(pady=10)

        tk.Label(self.content_frame, text="Калькулятор кредита", font=("Arial", 12, "bold")).pack(anchor="w",
                                                                                                  pady=(20, 5))
        tk.Label(self.content_frame, text="Сумма кредита (₽):").pack(anchor="w")
        cred_sum = tk.Entry(self.content_frame, width=30);
        cred_sum.pack()
        tk.Label(self.content_frame, text="Ставка (% годовых):").pack(anchor="w")
        cred_rate = tk.Entry(self.content_frame, width=30);
        cred_rate.pack()
        tk.Label(self.content_frame, text="Срок (месяцев):").pack(anchor="w")
        cred_months = tk.Entry(self.content_frame, width=30);
        cred_months.pack()

        def calc_credit():
            try:
                s = float(cred_sum.get())
                r = float(cred_rate.get())
                m = int(cred_months.get())
                pay, total = калькулятор_кредита(s, r, m)
                messagebox.showinfo("Результат", f"Ежемесячный платёж: {pay:,.2f} ₽\nОбщая сумма: {total:,.2f} ₽")
            except:
                messagebox.showerror("Ошибка", "Проверьте введённые данные")

        tk.Button(self.content_frame, text="Рассчитать кредит", command=calc_credit, width=25).pack(pady=10)

    def admin_view(self):
        self.show_content("Админ-панель", self._render_admin)

    def _render_admin(self):
        users = get_all_users()
        if not users:
            tk.Label(self.content_frame, text="Пользователи не найдены").pack()
            return
        for u in users:
            frame = tk.Frame(self.content_frame, relief="ridge", bd=1, padx=5, pady=5)
            frame.pack(fill="x", pady=2)
            tk.Label(frame, text=f"ID: {u[0]} | Логин: {u[1]} | ФИО: {u[2]} | Роль: {u[3]}").pack(side="left")
            tk.Button(frame, text="Удалить", fg="red", command=lambda uid=u[0]: self.delete_user_confirm(uid)).pack(
                side="right")

    def delete_user_confirm(self, uid):
        if messagebox.askyesno("Подтверждение", "Удалить пользователя? Это действие нельзя отменить!"):
            delete_user(uid)
            self.admin_view()


if __name__ == "__main__":
    root = tk.Tk()
    app = BankApp(root)
    root.mainloop()