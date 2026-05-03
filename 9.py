import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
import subprocess
from datetime import datetime

class PasswordGenerator:
    def __init__(self, master):
        self.master = master
        master.title("Random Password Generator")

        self.data_file = 'password_history.json'
        self.password_history = self.load_history()

        # --- Интерфейс ---
        self.main_frame = ttk.Frame(master, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Длина пароля
        ttk.Label(self.main_frame, text="Длина пароля:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.length_slider = ttk.Scale(self.main_frame, from_=4, to=128, orient=tk.HORIZONTAL, length=200)
        self.length_slider.set(12) # Значение по умолчанию
        self.length_slider.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.length_value_label = ttk.Label(self.main_frame, text=f"{int(self.length_slider.get())}")
        self.length_value_label.grid(row=0, column=2, padx=5)
        self.length_slider.bind("<Motion>", self.update_length_label)

        # Типы символов
        self.include_digits = tk.BooleanVar(value=True)
        self.include_letters = tk.BooleanVar(value=True)
        self.include_symbols = tk.BooleanVar(value=False)

        ttk.Checkbutton(self.main_frame, text="Цифры", variable=self.include_digits).grid(row=1, column=0, columnspan=1, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(self.main_frame, text="Буквы", variable=self.include_letters).grid(row=1, column=1, columnspan=1, padx=5, pady=2, sticky="w")
        ttk.Checkbutton(self.main_frame, text="Спецсимволы", variable=self.include_symbols).grid(row=1, column=2, columnspan=1, padx=5, pady=2, sticky="w")

        # Кнопка генерации
        self.generate_button = ttk.Button(self.main_frame, text="Сгенерировать пароль", command=self.generate_password)
        self.generate_button.grid(row=2, column=0, columnspan=3, padx=5, pady=10)

        # Сгенерированный пароль
        ttk.Label(self.main_frame, text="Пароль:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.password_display = ttk.Entry(self.main_frame, width=30, state='readonly')
        self.password_display.grid(row=3, column=1, columnspan=2, padx=5, pady=2, sticky="ew")

        # Таблица истории
        self.history_frame = ttk.LabelFrame(master, text="История паролей", padding="10")
        self.history_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.tree = ttk.Treeview(self.history_frame, columns=("Timestamp", "Password", "Length", "Digits", "Letters", "Symbols"), show="headings")
        self.tree.heading("Timestamp", text="Время")
        self.tree.heading("Password", text="Пароль")
        self.tree.heading("Length", text="Длина")
        self.tree.heading("Digits", text="Цифры")
        self.tree.heading("Letters", text="Буквы")
        self.tree.heading("Symbols", text="Симв.")
        self.tree.column("Timestamp", width=150)
        self.tree.column("Password", width=150)
        self.tree.column("Length", width=50, anchor='center')
        self.tree.column("Digits", width=50, anchor='center')
        self.tree.column("Letters", width=50, anchor='center')
        self.tree.column("Symbols", width=50, anchor='center')
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self.history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.update_history_table()

    def update_length_label(self, event):
        length = int(self.length_slider.get())
        self.length_value_label.config(text=str(length))

    def load_history(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def save_history(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.password_history, f, indent=4, ensure_ascii=False)

    def generate_password(self):
        length = int(self.length_slider.get())
        include_digits = self.include_digits.get()
        include_letters = self.include_letters.get()
        include_symbols = self.include_symbols.get()

        if not include_digits and not include_letters and not include_symbols:
            messagebox.showwarning("Внимание", "Выберите хотя бы один тип символов.")
            return

        characters = ""
        if include_digits:
            characters += string.digits
        if include_letters:
            characters += string.ascii_letters
        if include_symbols:
            characters += string.punctuation

        if length < 4 or length > 128:
            messagebox.showwarning("Некорректный ввод", "Длина пароля должна быть от 4 до 128 символов.")
            return

        try:
            password = ''.join(random.choice(characters) for _ in range(length))
            self.password_display.config(state='normal')
            self.password_display.delete(0, tk.END)
            self.password_display.insert(0, password)
            self.password_display.config(state='readonly')

            # Добавляем в историю
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.password_history.append({
                "timestamp": timestamp,
                "password": password,
                "length": length,
                "digits": include_digits,
                "letters": include_letters,
                "symbols": include_symbols
            })
            self.save_history()
            self.update_history_table()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при генерации: {e}")

    def update_history_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for record in reversed(self.password_history):
            self.tree.insert("", tk.END, values=(
                record.get("timestamp"),
                record.get("password"),
                record.get("length"),
                "Да" if record.get("digits") else "Нет",
                "Да" if record.get("letters") else "Нет",
                "Да" if record.get("symbols") else "Нет"
            ))

# --- Функции Git ---
def setup_git_repo(repo_path="."):
    if not os.path.exists(os.path.join(repo_path, ".git")):
        subprocess.run(["git", "init"], cwd=repo_path, check=True)
        print("Git репозиторий инициализирован.")
    else:
        print("Git репозиторий уже существует.")

def create_gitignore(repo_path="."):
    gitignore_path = os.path.join(repo_path, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write("__pycache__/\n")
            f.write("*.pyc\n")
            f.write("password_history.json\n") # Не добавлять файл с историей в Git
        print(".gitignore создан.")


if __name__ == "__main__":
    setup_git_repo()
    create_gitignore()

    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()
